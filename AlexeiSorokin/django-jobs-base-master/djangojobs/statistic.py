import sys
from settings import BASE_DIR
sys.path.append(BASE_DIR)

from collections import Counter
from sqlalchemy.orm import sessionmaker

from djangojobs.models import *


class QueriesBase(object):
    """
    Queries base class.
    """
    def __init__(self, source=None):
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)

        if source is not None:
            self.Source = source


class VacancyQueries(QueriesBase):
    """
    Counting None types and tracebacks in found results for Vacancy table.
    """
    # TODO: NEVER TESTED!
    def __init__(self, source):
        super(QueriesBase, self).__init__(source)

    def none_types(self, obj):
        none_types = Counter({
            'title': 0,
            'work_schedule': 0,
            'required_skills': 0,
            'desired_skills': 0,
            'description': 0,
            'date': 0,
            'qualification_level': 0,
            'link': 0,
            'salary': 0
        })

        if obj.title is None:
            none_types['title'] += 1
        if obj.work_schedule is None:
            none_types['work_schedule'] += 1
        if obj.required_skills is None:
            none_types['required_skills'] += 1
        if obj.desired_skills is None:
            none_types['desired_skills'] += 1
        if obj.description is None:
            none_types['description'] += 1
        if obj.date is None:
            none_types['date'] += 1
        if obj.qualification_level is None:
            none_types['qualification_level'] += 1
        if obj.link is None:
            none_types['link'] += 1

        return none_types

    def count_statistic(self):
        objs = session.query(Vacancy).filter_by(source=self.Source)

        with_tracebacks = session.query(Vacancy).filter_by(tracebacks=True)
        without_tracebacks = session.query(Vacancy).filter_by(tracebacks=False)

        none_types = Counter({})

        if objs:
            for obj in objs:
                obj_none_types = self.none_types(obj)

                none_types = none_types + obj_none_types

        return with_tracebacks, without_tracebacks, none_types


class CompanyQueries(QueriesBase):
    """
    Counting None types and tracebacks in found results for Company.
    """
    def __init__(self):
        super(QueriesBase, self).__init__()

    def none_types(self, obj):
        none_types = Counter({
            'name': 0,
            'country': 0,
            'state': 0,
            'city': 0,
            'website': 0,
            'email': 0,
            'phone': 0
        })

        if obj.name is None:
            none_types['name'] += 1
        if obj.country is None:
            none_types['country'] += 1
        if obj.state is None:
            none_types['state'] += 1
        if obj.city is None:
            none_types['city'] += 1
        if obj.website is None:
            none_types['website'] += 1
        if obj.email is None:
            none_types['email'] += 1
        if obj.phone is None:
            none_types['phone'] += 1

        return none_types

    def count_statistic(self):
        objs = session.query(Company)

        with_tracebacks = session.query(Company).filter_by(tracebacks=True)
        without_tracebacks = session.query(Company).filter_by(tracebacks=False)

        none_types = Counter({})

        if objs:
            for obj in objs:
                obj_none_types = self.none_types(obj)

                none_types = none_types + obj_none_types

        return none_types, with_tracebacks, without_tracebacks
