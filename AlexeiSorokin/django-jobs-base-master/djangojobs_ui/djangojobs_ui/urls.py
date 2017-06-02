"""djangojobs_ui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from class_based_auth_views.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.base import RedirectView


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/login/$',
        LoginView.as_view(form_class=AuthenticationForm,
                         success_url='success'),
        name='login'),
    url(r'^accounts/login/success/$',
        RedirectView.as_view(url='/', permanent=False)),
    url(r'^accounts/logout/$',
        LogoutView.as_view(),
        name='logout'),

    url(r'', include('userinterface.urls')),
]
