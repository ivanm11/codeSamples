# -*- coding: utf-8 -*-
import re
import scrapy

from datetime import datetime

from djangojobs.items import *

from utils import G, search_skills


class FlexjobsSpider(scrapy.Spider):
    # TODO: TEST IT CAREFULLY!!!
    name = "flexjobs"
    allowed_domains = ["flexjobs.com"]
    start_urls = ['https://www.flexjobs.com/search?search=django']
    SOURCE = 'flexjobs'
    BASE_URL = 'http://flexjobs.com'

    def get_listed_info(self, job):
        vacancy_item = VacancyItem()
        company_item = CompanyItem()

        work_schedule, job_city, job_state, \
                telecommunicate, vacancy_date = (None,) * 5

        job_block = G(job.xpath\
            ('div[@class="row"]//div[@class="row"]/div[@class="col-sm-6"]'), 0)
        date_block = G(job.xpath\
            ('div[@class="row"]/div[@class="col-sm-1 col-xs-2"]'), 0)

        if job_block is not None:
            job_link = G(job_block.xpath('h5/a/@href').extract(), 0)
            if job_link is not None:
                job_link = self.BASE_URL + job_link

            job_title = G(job_block.xpath('h5/a/text()').extract(), 0)
            job_location = G(job_block.xpath\
                ('p[@class="job-type-info"]/text()').extract(), 0)

            if job_location is not None:
                if ',' in job_location:
                    job_location = job_location.split(',')
                    if len(job_location) == 2:
                        if len(job_location[1]) == 2:
                            job_state = job_location[1]
                    job_city = job_location[0]
                else:
                    job_city = job_location

            schedule_block = G(job_block.xpath\
                ('p[@class="job-type-info"]/span[@class="text-danger"]/text()')\
                               .extract(), 0)
            if schedule_block is not None:
                schedule_block = schedule_block.lower()
                if 'part-time' in schedule_block:
                    work_schedule = 'Part-Time'
                elif 'full-time' in schedule_block:
                    work_schedule = 'Part-Time'

                if re.search(r'remote|telecomm', schedule_block):
                    telecommunicate = True

        if date_block is not None:
            vacancy_date = G(date_block.xpath('p/small/text()').extract(), 0)
            if vacancy_date is not None:
                today = datetime.today()
                vacancy_date = vacancy_date + ' ' + str(today.year)
                vacancy_date = datetime.strptime(vacancy_date, '%b %d %Y')

        vacancy_item['link'] = job_link
        vacancy_item['title'] = job_title
        # vacancy_item['city'] = job_city
        # vacancy_item['state'] = job_state
        vacancy_item['telecommunicate'] = telecommunicate
        vacancy_item['work_schedule'] = work_schedule
        vacancy_item['source'] = self.SOURCE
        vacancy_item['date'] = vacancy_date

        return vacancy_item, company_item

    def get_details(self, response):
        vacancy_item = response.meta['vacancy_item']
        company_item = response.meta['company_item']

        job_description_block = response.xpath('//div[@id="job-description"]')

        if len(job_description_block) == 2:
            job_details_block = job_description_block[1]
            job_description_block = job_description_block[0]

            job_details_sections = job_details_block.xpath\
                ('//div[@class="table-responsive"]/tr')

            for job in job_details_sections:
                job_header = G(job.xpath('th/text()').extract(), 0)
                if job_header is not None:
                    if 'date' in job_header.lower():
                        job_date = G(job.xpath('td/text()').extract(), 0)
                        if job_date is not None:
                            job_date = datetime.strptime('%m/%d/%Y')
                            vacancy_item['date'] = job_date
                            continue

                    elif 'location' in job_header.lower():
                        location_string = G(job.xpath('td/text()').extract(),
                                            0)
                        if location_string is not None:
                            location_list = location_string.split(',')
                            if len(location_list) == 2:
                                vacancy_item['city'] = location_list[0]
                                vacancy_item['country'] = location_list[1]
                            elif len(location_list) == 3:
                                vacancy_item['city'] = location_list[0]
                                if len(location_list[1]) in range(2, 4):
                                    vacancy_item['state'] == location_list[1]
                                location_item['country'] = location_list[2]
                            continue

                    elif re.search(r'telecomm', job_header, re.I):
                        vacancy_item['telecommunicate'] = True
                        continue

                    elif 'type' in job_header.lower():
                        job_type = G(job.xpath('td/text()').extract(), 0)
                        if job_type is not None:
                            if 'part-time' in job_type.lower():
                                vacancy_item['work_schedule'] = 'Part-Time'
                            elif 'full-time' in job_type.lower():
                                vacancy_item['work_schedule'] = 'Full-Time'

            job_description_text = job_description_block.xpath\
                ('div[@class="col-lg-9"]/div[@class="well well-sm"]/p/text()')\
                    .extract()

            if G(job_description_text, 0) is not None:
                skills_list = search_skills(job_description_text)

        return vacancy_item, company_item

    def parse(self, response):
        listed_jobs = response.xpath('//ul[@id="joblist"]/li')
        if listed_jobs:
            for job in listed_jobs:
                vacancy_item, company_item = self.get_listed_info(job)
                yield scrapy.Request(vacancy_item['link'],
                                     meta = {'vacancy_item': vacancy_item,
                                             'company_item': company_item},
                                     callback = self.get_details)

