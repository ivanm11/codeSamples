from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from userinterface.models import Company, Vacancy


class DjangoJobsStatistics(object):

    AVAILABLE_SOURCES = {
        'djangojobs': 'http://djangojobs.net/jobs/',
        'indeed': 'https://www.indeed.com/q-Django-jobs.html',

        'stackoverflow': \
        'http://stackoverflow.com/jobs/developer-jobs-using-django',

        'technojobs': 'https://www.technojobs.co.uk/django-jobs/',
        'github': 'https://jobs.github.com/positions?description=django',
        'mashable': 'http://jobs.mashable.com/jobs/results/keyword/django',
        'flexjobs': 'https://www.flexjobs.com/search?search=django',
    }

    def __init__(self):
        now = datetime.now()
        self.month = now.strftime('%m')
        self.week = now.isocalendar()[1]

    def company_statistic(self):
        company_stats = {
            'all_records': len(Company.objects.all()),
            'no_name': len(Company.objects.filter(name=None)),
            'no_country': len(Company.objects.filter(country=None)),
            'no_state': len(Company.objects.filter(state=None)),
            'no_city': len(Company.objects.filter(city=None)),
            'no_website': len(Company.objects.filter(website=None)),
            'no_email': len(Company.objects.filter(email=None)),
            'no_phone': len(Company.objects.filter(phone=None)),
            'has_managed': len(Company.objects.filter(is_managed=True)),
        }

        return company_stats

    def vacancy_statistic(self):
        vacancy_stats = {
            'all_records': len(Vacancy.objects.all()),
            'no_title': len(Vacancy.objects.filter(title=None)),
            'no_schedule': len(Vacancy.objects.filter(work_schedule=None)),
            'no_telecommunicate':
                len(Vacancy.objects.filter(telecommunicate=None)),
            'no_is_expired': len(Vacancy.objects.filter(is_expired=None)),
            'no_required': len(Vacancy.objects.filter(required_skills=None)),
            'no_desired': len(Vacancy.objects.filter(desired_skills=None)),
            'no_desc': len(Vacancy.objects.filter(description=None)),
            'no_date': len(Vacancy.objects.filter(date=None)),
            'no_level': len(Vacancy.objects.filter(qualification_level=None)),
            'no_source': len(Vacancy.objects.filter(source=None)),
            'no_link': len(Vacancy.objects.filter(link=None)),
            'no_salary': len(Vacancy.objects.filter(salary=None)),
        }

        for source, link in self.AVAILABLE_SOURCES.iteritems():
            try:
                latest = Vacancy.objects.filter(source=source).latest('added')
                last_time_count = len(Vacancy.objects.filter(source=source,
                                                       added__date=latest.added.date()))
            except ObjectDoesNotExist:
                last_time_count = 0

            vacancy_stats[source] = {
                'overall': len(Vacancy.objects.filter(source=source)),
                'this_month': len(Vacancy.objects.filter(source=source,
                                                         added__month=self.month)),
                'this_week': len(Vacancy.objects.filter(source=source,
                                                        added__week=self.week)),
                'last_time_count': last_time_count,
                'last_time_runned': latest.added# .replace(second=0,
                                                #         microsecond=0),
            }

        return vacancy_stats

    #def leads_statistic(self):
    #    leads_stats = {
    #        'all_records': len(Lead.objects.all()),
    #        'no_first_name': len(Lead.objects.filter(first_name=None)),
    #        'no_last_name': len(Lead.objects.filter(last_name=None)),
    #        'no_country': len(Lead.objects.filter(country=None)),
    #        'no_email': len(Lead.objects.filter(email=None)),
    #        'no_capture_link': len(Lead.objects.filter(capture_link=None)),
    #        'no_phone': len(Lead.objects.filter(phone=None)),
    #        'no_source': len(Lead.objects.filter(source=None)),
    #        'no_vacancy_link': len(Lead.objects.filter(vacancy_link=None)),
    #        'no_vacancy_name': len(Lead.objects.filter(vacancy_name=None)),
    #        'no_company_link': len(Lead.objects.filter(company_link=None)),
    #        'no_company_name': len(Lead.objects.filter(company_name=None)),
    #    }

    #    return leads_stats

