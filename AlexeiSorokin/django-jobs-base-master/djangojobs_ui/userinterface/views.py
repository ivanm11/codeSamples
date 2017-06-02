# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from userinterface.models import Company, Vacancy, Errors
from userinterface.utils import DjangoJobsStatistics


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class VacanciesView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('login')
        objs = Vacancy.objects.all()
        return render(request, 'userinterface/vacancies.html', {'vacancies': objs})


class CompaniesView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('login')
        objs = Company.objects.all()
        return render(request,
                      'userinterface/companies.html',
                      {'companies': objs})


class LeadsView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('login')
        objs = Company.objects.filter(lead_data__isnull=False)
        return render(request,
                      'userinterface/leads.html',
                      {'leads': objs})


class ErrorsView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('login')
        objs = Errors.objects.all()
        return render(request,
                      'userinterface/errors.html',
                      {'errors': objs})


class LastFoundVacanciesView(View):
    def get(self, request, start_id, end_id):
        if not request.user.is_authenticated():
            return redirect('login')
        objs = Vacancy.objects.filter(id__range=(start_id, end_id))
        return render(request,
                      'userinterface/vacancies.html',
                      {'vacancies': objs})


class LastFoundCompaniesView(View):
    def get(self, request, start_id, end_id):
        if not request.user.is_authenticated():
            return redirect('login')
        objs = Company.objects.filter(id__range=(start_id, end_id))
        return render(request,
                      'userinterface/companies.html',
                      {'companies': objs})


class ManuallyEditedCompaniesView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('login')
        objs = Company.objects.filter(is_managed=True)
        return render(request,
                      'userinterface/companies.html',
                      {'companies': objs})


class StatisticView(View):
    def get(self, request):
        if not request.user.is_authenticated():
            return redirect('login')
        stats = DjangoJobsStatistics()
        sources = stats.AVAILABLE_SOURCES
        company_stats = stats.company_statistic()
        vacancy_stats = stats.vacancy_statistic()
        # leads_stats = stats.leads_statistic()
        return render(request,
                      'userinterface/statistic.html',
                      {'sources': sources,
                       'company_stats': company_stats,
                       'vacancy_stats': vacancy_stats,})
                       # 'leads_stats': leads_stats})


class CompanyPageView(View):
    def get(self, request, company_name):
        if not request.user.is_authenticated():
            return redirect('login')
        company_name = self._real_company_name(company_name)
        company_obj = Company.objects.get(name__icontains=company_name)
        # lead_objs = Lead.objects.filter(company_name__icontains=company_name)
        return render(request,
                      'userinterface/company.html',
                      {'obj': company_obj,})
                       # 'leads': lead_objs})

    def post(self, request, company_name):
        if not request.user.is_authenticated():
            return redirect('login')

        new_company_name = request.POST.get('company_name', '')
        new_country = request.POST.get('country', '')
        new_state = request.POST.get('state', '')
        new_city = request.POST.get('city', '')
        new_website = request.POST.get('website', '')
        new_email = request.POST.get('email', '')
        new_phone = request.POST.get('phone', '')

        company_name = self._real_company_name(company_name)

        try:
            obj = Company.objects.get(name__icontains=company_name)
        except ObjectDoesNotExist:
            raise Exception

        if new_company_name:
            obj.company_name = new_company_name
        if new_country:
            obj.country = new_country
        if new_state:
            obj.state = new_state
        if new_city:
            obj.city = new_city
        if new_website:
            obj.website = new_website
        if new_email:
            obj.email = new_email
        if new_phone:
            obj.phone = new_phone

        if any([new_company_name, new_country, new_state, new_city,
                new_website, new_email, new_phone]):
            obj.is_managed = True
            obj.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def _real_company_name(self, company_name):
        return company_name.replace('_', ' ').replace('%', '.')\
                .replace('$', ',').lower()

