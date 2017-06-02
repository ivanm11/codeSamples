import json

from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from djangojobs.models import *
from djangojobs.items import *
from spiders.utils import DjangojobsError


class QueriesBase(object):
    """
    Database queries base class.
    """
    def __init__(self, source=None):
        try:
            engine = db_connect()
        except ValueError:
            raise DjangojobsError('Undefined database. ' + \
                                  'Check your local_settings.py')

        create_tables(engine)
        self.Session = sessionmaker(bind=engine)


class PostgresPipeline(QueriesBase):
    """
    Pipeline for storing scraped items in the database.
    """
    def __init__(self):
        super(PostgresPipeline, self).__init__()

    def process_item(self, item, spider):
        session = self.Session()
        if item._table_name() == 'company':
            prepared = Company(**item)
        elif item._table_name() == 'vacancy':
            prepared = Vacancy(**item)
        else:
            raise Exception
        
        if self._get_item(session, prepared) is False:
            self._add_item(session, prepared)
        else:
            self._update_item(session, prepared)

        session.close()

    def _add_item(self, session, model):
        if model.__class__.__name__ == 'Company':
            self._update_lead_data(session, model)

        try:
            session.add(model)
            session.commit()
        except:
            session.rollback()
            raise Exception
        return

    def _get_item(self, session, model):
        record_exists = False

        if model.__class__.__name__ == 'Company':
            record_exists = session.query\
                    (exists().where(Company.name == model.name)).scalar()
        elif model.__class__.__name__ == 'Vacancy':
            record_exists = session.query\
                    (exists().where(and_(Vacancy.title == model.title,
                                    Vacancy.source == model.source))).scalar()
        else:
            # TODO: impossible?
            raise Exception

        return record_exists

    def _update_item(self, session, model):
        # TODO: test it carefully!
        updated = False
        if model.__class__.__name__ == 'Vacancy':
            columns = Vacancy.__table__.columns.keys()
            query = session.query(Vacancy).filter(and_\
                    (Vacancy.title == model.title,\
                     Vacancy.source == model.source))

            if len(query.all()) > 1:
                # TODO: impossible?
                raise Exception

            obj = query.first()

            if obj is None:
                # TODO: impossible?
                raise Exception

            for column in columns:
                if column not in ('id', 'lead_id', 'date', 'link', 'added'):
                    new_value = getattr(model, column)
                    if getattr(obj, column) != new_value:
                        setattr(obj, column, new_value)
                        session.commit()
                        updated = True

            if updated is True:
                setattr(obj, 'added', datetime.now())

        #if model.__class__.__name__ == 'Company':
        #    query = session.query(Company).filter(Company.name == model.name)
        #    lead_data = query.first().lead_data
        #    if lead_data and hasattr(model, 'lead_data'):
        #        if lead_data != model.lead_data:

        if model.__class__.__name__ == 'Company':
            self._update_lead_data(session, model)

        return

    def _update_lead_data(self, session, model):
        # TODO: TEST IT!!!
        # TODO: will be much better to store vacancies as ['name': 'link']
        # FIXME: looks so ugly, a lot of same code repeats
        if not model.__class__.__name__ == 'Company':
            raise Exception

        query = session.query(Company).filter(Company.name == model.name)
        obj = query.first()

        if not obj and hasattr(model, 'lead_data'):
            model.lead_data = json.dumps({'leads': [model.lead_data]})

        elif not obj.lead_data and hasattr(model, 'lead_data'):
            model.lead_data = json.dumps({'leads': [model.lead_data]})

        elif obj.lead_data and hasattr(model, 'lead_data'):
            lead_data_old = json.loads(obj.lead_data)
            leads = lead_data_old['leads']

            if None not in leads and model.lead_data is not None:
                for num, lead in enumerate(leads):

                    if lead['first_name'] is not None and lead['last_name'] is not None:
                        if lead['first_name'] == model.lead_data['first_name'] and \
                            lead['last_name'] == model.lead_data['last_name']:
                            if model.lead_data['vacancy_link'][0] is not None:
                                if model.lead_data['vacancy_link'][0] not in lead['vacancy_link']:
                                    lead_data_old['leads'][num]['vacancy_link'].append(model.lead_data['vacancy_link'][0])
                                    obj.lead_data = json.dumps(lead_data_old)
                                    session.commit()
                                    break

                    elif lead['last_name'] is not None:
                        if lead['last_name'] == model.lead_data['last_name']:
                            if model.lead_data['vacancy_link'][0] is not None:
                                if model.lead_data['vacancy_link'][0] not in lead['vacancy_link']:
                                    lead_data_old['leads'][num]['vacancy_link'].append(model.lead_data['vacancy_link'][0])
                                    obj.lead_data = json.dumps(lead_data_old)
                                    session.commit()
                                    break

                    elif lead['email'] is not None:
                        if lead['email'] == lead_data_old['email']:
                            if lead['email'] not in lead_data_old.email:
                                lead_data_old['leads'][num]['vacancy_link'].append(lead['vacancy_link'][0])
                                obj.lead_data = json.dumps(lead_data_old)
                                session.commit()
                                break

        return

