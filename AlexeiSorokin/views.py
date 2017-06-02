import datetime
import time
import io
import csv

from rest_framework import generics, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import JSONWebTokenSerializer, RefreshJSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework_jwt.utils import jwt_decode_handler
from accounts.api.utils.jwt import jwt_payload_handler
from accounts.api.v1.serializers import UserFullSerializer
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from jwt.exceptions import ExpiredSignatureError

from accounts.licensing.util import increment_limitable_feature_usage
from accounts.models import CustomUser
from accounts.licensing.models import ProductFeatureDailyCounter, LicensingWarning
from accounts.licensing.util import get_usage_count_from_db, check_record_limit

from logger import logger
from . import serializers

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError

from accounts.api.utils import email_helper


jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class JSONWebTokenBase(object):
    """
    Modified standard JWT methods.
    """

    def get_request_data(self, request):
        if hasattr(request, 'data'):
            data = request.data
        elif hasattr(request, 'DATA'):
            data = request.DATA
        else:
            data = None
        return data


class ObtainJSONWebToken(JSONWebTokenAPIView, JSONWebTokenBase):
    """
    API View that receives a POST with a user's username and password.
    Returns a JSON Web Token that can be used for authenticated requests.
    """
    serializer_class = JSONWebTokenSerializer

    def post(self, request):
        data = self.get_request_data(request)

        if data is None:
            return Response({'error': 'No data in response'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            data=data
        )

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)

            try:
                increment_limitable_feature_usage(user, 'SIGN_IN', used=1)
            except AttributeError:
                return Response({u'non_field_errors': [u'In order to log in, user should belong to Organization. Please contact support team.']},
                        status=status.HTTP_400_BAD_REQUEST)

            warnings = LicensingWarning.objects.filter(user=user, seen=False)
            for warning in warnings:
                warning.seen = True
                warning.save()

            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    authentication_classes = (JSONWebTokenAuthentication,
                              SessionAuthentication,)
    permission_classes = [
        permissions.AllowAny
    ]

    serializer_class = serializers.ResetPasswordSerializer

    def put(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')

        try:
            uid = urlsafe_base64_decode(uidb64)
            user = CustomUser.objects.get(pk=uid)
            if user and default_token_generator.check_token(user, token):
                serializer = serializers.ResetPasswordSerializer(user)
                serializer.save(validated_data=request.data, instance=user)
                payload = jwt_payload_handler(user)
                return Response({'token': jwt_encode_handler(payload)})
            else:
                return Response({'non_field_errors': 'Password reset has expired'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError) as e:
            logger.exception(e)
            return Response(status=status.HTTP_404_NOT_FOUND)


class PasswordResetRequestView(generics.GenericAPIView):
    authentication_classes = (JSONWebTokenAuthentication,
                              SessionAuthentication,)
    permission_classes = [
        permissions.AllowAny
    ]

    serializer_class = serializers.ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save(validated_data=request.data)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(generics.CreateAPIView):
    """
    POST /api/v1/account/token/register/
    """
    authentication_classes = (JSONWebTokenAuthentication,
                              SessionAuthentication,)
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = serializers.UserCreateSerializer


class MaskBase(object):
    """
    Base class for mask methods.
    """

    def get_http_auth_token(self, request):
        if not 'HTTP_AUTHORIZATION' in request.META:
            raise ValidationError({'No HTTP_AUTHORIZATION in request.META'})
        return request.META['HTTP_AUTHORIZATION'][4:]

    def encode_token(self, payload):
        payload = jwt_payload_handler(payload)
        return jwt_encode_handler(payload)

    def decode_token(self, token):
        return jwt_decode_handler(token)


class RefreshJSONWebToken(JSONWebTokenAPIView, MaskBase, JSONWebTokenBase):
    """
    GET /api/v1/account/token/refresh/
    POST /api/v1/account/token/refresh/
    """
    
    serializer_class = RefreshJSONWebTokenSerializer

    def post(self, request):
        
        data = self.get_request_data(request)

        if data is None:
            return Response(data={'error': 'No data in response'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
                data=data
        )
        
        if serializer.is_valid():
            try:
                payload = self.decode_token(data['token'])
            except ExpiredSignatureError:
                return Response(data={'error': 'Expired token'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.object.get('user') or request.user

            if 'is_masked' in payload:
                token = self.encode_token(payload)
            else:
                token = serializer.object.get('token')

            response_data = jwt_response_payload_handler(token, user, request)
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class MaskUser(generics.GenericAPIView, MaskBase):
    """
    POST /api/v1/account/mask-user/
    """
    
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
 
    def post(self, request, format=None):
        if 'email' in request.data:
            email = request.data.get('email')
            if not CustomUser.objects.get(email=request.user.email).is_staff:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Only admin users allowed'})

            try:
                masked_user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist as e:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No user with %s email' % email})

            original_payload = self.decode_token(self.get_http_auth_token(request))
            masked_payload = UserFullSerializer(masked_user).data

            if 'original_user' not in original_payload:
                masked_payload['original_user'] = original_payload['email']
            else:
                masked_payload['original_user'] = original_payload['original_user']

            masked_payload['is_masked'] = True
            masked_payload['is_staff'] = True

            masked_user_token = self.encode_token(masked_payload)
            
            return Response({'token': masked_user_token})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No user email in request'})

    def get_queryset(self):
        return CustomUser.objects.all()


class UnmaskUser(generics.GenericAPIView, MaskBase):
    """
    POST /api/v1/account/unmask-user/
    """

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,) 
    
    def post(self, request, format=None):
        payload = self.decode_token(self.get_http_auth_token(request))
        if 'original_user' in payload:
            payload['email'] = payload['original_user']
            try:
                user = CustomUser.objects.get(email=payload['original_user'])
            except CustomUser.DoesNotExist as e:
                logger.exception(e)
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No user with %s email' % payload['original_user']})
           
            token = self.encode_token(user)
            del payload['original_user']
            del payload['is_masked']
            return Response({'token': token})

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No original_user in payload'})


class UserListView(generics.ListAPIView, MaskBase):
    """
    GET /api/v1/account/users/
    """

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserFullSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(organization_id=self.request.user.organization_id).select_related(
            'organization')


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    PUT /api/v1/account/users/<user_id>/
    """

    authentication_classes = (JSONWebTokenAuthentication,
                              SessionAuthentication)

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserFullSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(organization_id=self.request.user.organization_id)


def reports_beta(request):

    def _get_product_last_used(organization, product_name):
        pfdc = ProductFeatureDailyCounter.objects.filter(organization=organization,
                                                         feature__product__name=product_name)\
            .exclude(counter=0).order_by('date').last()

        if not pfdc:
            return None

        return pfdc.date.strftime("%Y-%m-%d %H:%M:%S")

    if request.GET.get('beta') != 'false':
        users = CustomUser.objects.filter(pk__gt=0, organization__is_beta=True)
    else:
        users = CustomUser.objects.filter(pk__gt=0)

    headers = [
        u'account_id',
        u'username',
        u'last_login',
        u'logins_count',
        u'dc_last_used',
        u'dc_run_match_count',
        u'uu_last_used',
        u'uu_run_match_count',
        u'w2l_last_used',
        u'w2l_submissions'
    ]

    today = datetime.datetime.now().date()
    week_delta = datetime.timedelta(days=7)
    range_start = today - week_delta
    range_end = today

    with io.BytesIO() as f:
        csv_writer = csv.DictWriter(f, headers)
        csv_writer.writeheader()

        for user in users:
            user_dict = {
                'account_id': user.organization.rl_salesforce_account_id,
                'username': user.email,
                'last_login': user.last_client_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_client_login else '',
                'logins_count': get_usage_count_from_db(user.organization, 'GENERAL', 'SIGN_IN', range_start,
                                                        range_end),
                'dc_last_used': _get_product_last_used(user.organization, 'DC'),
                'uu_last_used': _get_product_last_used(user.organization, 'UU'),
                'dc_run_match_count': get_usage_count_from_db(user.organization, 'DC', 'RUN_MATCH', range_start,
                                                              range_end),
                'uu_run_match_count': get_usage_count_from_db(user.organization, 'UU', 'RUN_MATCH', range_start,
                                                              range_end),
                'w2l_last_used': _get_product_last_used(user.organization, 'W2L'),
                'w2l_submissions': 0
            }
            print '=' * 50
            print u'User {}'.format(user.email)
            print user_dict
            print '=' * 50
            csv_writer.writerow(user_dict)
        f.seek(0)
        wrapper = FileWrapper(f)
        response = HttpResponse(wrapper, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=reports_beta_'+time.strftime("%Y%m%d-%H%M%S")+'.csv'

        return response

