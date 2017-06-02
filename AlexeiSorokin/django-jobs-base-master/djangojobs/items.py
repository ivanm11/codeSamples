# -*- coding: utf-8 -*-

from scrapy import Item, Field


class CompanyItem(Item):
    name = Field()
    country = Field()
    state = Field()
    city = Field()
    website = Field()
    email = Field()
    phone = Field()
    lead_data = Field()

    def _table_name(self):
        return 'company'

class VacancyItem(Item):
    title = Field()
    work_schedule = Field()
    required_skills = Field()
    desired_skills = Field()
    description = Field()
    date = Field()
    qualification_level = Field()
    salary = Field()
    source = Field()
    link = Field()
    is_expired = Field()
    telecommunicate = Field()

    def _table_name(self):
        return 'vacancy'

