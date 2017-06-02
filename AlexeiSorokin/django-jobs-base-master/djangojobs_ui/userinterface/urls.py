from django.conf.urls import url

from views import *


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^vacancies/$', VacanciesView.as_view(), name='vacancies'),
    url(r'^companies/$', CompaniesView.as_view(), name='companies'),
    url(r'^leads/$', LeadsView.as_view(), name='leads'),
    url(r'^errors/$', ErrorsView.as_view(), name='errors'),
    url(r'^statistic/$', StatisticView.as_view(), name='statistic'),
    url(r'^edited-companies/$', ManuallyEditedCompaniesView.as_view(),
        name='edited-companies'),
    url(r'^found-companies/(?P<start_id>\d+)-(?P<end_id>\d+)/$', LastFoundCompaniesView.as_view(),
        name='found-companies'),
    url(r'^found-vacancies/(?P<start_id>\d+)-(?P<end_id>\d+)/$', LastFoundVacanciesView.as_view(),
        name='found-vacanies'),
    url(r'^(?P<company_name>[\w\/\_\$\%\-\(\)\&]+)/$', CompanyPageView.as_view(),
        name='company-page'),
]

