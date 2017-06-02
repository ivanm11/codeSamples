from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
                                Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from sqlalchemy.engine.url import URL

import settings

from datetime import datetime


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


def create_tables(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


#class Source(DeclarativeBase):
#    """
#    Sqlalchemy Source model.
#    """
#    __tablename__ = 'source'
#
#    id = Column(Integer, primary_key=True)
#    name = Column('name', String(255))
#    company = relationship('Company', back_populates='name')

class Company(DeclarativeBase):
    """
    Sqlalchemy Company model
    """
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
#    source_id = Column(Integer, ForeignKey('source.id'))
    name = Column('name', String)
    country = Column('country', String)
    state = Column('state', String, nullable=True)
    city = Column('city', String)
    website = Column('website', String)
    email = Column('email', String)
    phone = Column('phone', String)
    is_managed = Column('is_managed', Boolean, default=False, nullable=False)
    lead_data = Column('lead_data', JSON)
    added = Column('added', DateTime, default=datetime.now())
    vacancy = relationship('Vacancy')


class Vacancy(DeclarativeBase):
    """
    Sqlalchemy Vacancy model
    """
    __tablename__ = 'vacancy'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id'))
    title = Column('title', String)
    work_schedule = Column('work_schedule', String, nullable=True)
    required_skills = Column('required_skills', String)
    desired_skills = Column('desired_skills', String, nullable=True)
    description = Column('description', String)
    date = Column('date', DateTime)
    qualification_level = Column('qualification_level', String, nullable=True)
    salary = Column('salary', String, nullable=True)
    source = Column('source', String)
    link = Column('link', String)
    telecommunicate = Column('telecommunicate', Boolean)
    is_expired = Column('is_expired', Boolean)
    added = Column('added', DateTime, default=datetime.now())


class Errors(DeclarativeBase):
    """
    Sqlalchemy Errors model
    """
    __tablename__ = 'errors'

    id = Column(Integer, primary_key=True)
    vacancy_link = Column('vacancy_link', String)
    source = Column('source', String)
    file_name = Column('file_name', String)
    error_type = Column('error_type', String)
    error_message = Column('error_message', String)
    error_lineno = Column('error_lineno', Integer)
    error_datetime = Column('error_datetime', DateTime)

