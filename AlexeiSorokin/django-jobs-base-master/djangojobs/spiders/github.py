# -*- coding: utf-8 -*-
import pycountry
import re
import scrapy

from djangojobs.items import *
from utils import G, remove_whitespaces, qualification_from_title


class GithubSpider(scrapy.Spider):
    """
    jobs.github.com/positions?description=django crawler
    """
    name = "github"
    allowed_domains = ["github.com"]
    start_urls = ['https://jobs.github.com/positions?description=django']
    BASE_URL = 'https://jobs.github.com'
    SOURCE = 'github'

    def get_details(self, response):
        vacancy_item = response.meta['vacancy']
        company_item = response.meta['company']
        company_link = G(response.xpath('//div[@class="column ' + \
                            'sidebar"]//p[@class="url"]/a/@href').extract(), 0)

        if company_link is not None:
            company_item['website'] = company_link

        return vacancy_item, company_item

    def parse_in_list(self, job):
        vacancy_item = VacancyItem()
        company_item = CompanyItem()

        country, city, state, qualification_level = (None,) * 4

        title_block = job.xpath("td[@class='title']")
        meta_block = job.xpath("td[@class='meta']")
        job_title = G(title_block.xpath("h4/a/text()").extract(), 0)
        job_link = G(title_block.xpath("h4/a/@href").extract(), 0)
        company_name = \
            G(title_block.xpath("p[@class='source']/a/text()").extract(), 0)
        company_link = \
            G(title_block.xpath("p[@class='source']/a/@href").extract(), 0)
        work_schedule = \
            G(title_block.xpath("p[@class='source']/strong/text()")\
              .extract(), 0)

        location = \
            G(meta_block.xpath("span[@class='location']/text()").extract(), 0)

        if location is not None:
            location = location.split(",")
            if len(location) == 2:
                city = location[0]
                country = location[1].strip()
                if country.isupper() and len(country) == 2:
                    state = country
                    country = "United States"

            elif len(location) == 1:
                try:
                    pycountry.countries.get(name=location[0])
                    country = location[0]
                except KeyError:
                    pass

            elif len(location) > 2:
                for l in location:
                    try:
                        pycountry.countries.get(name=l)
                        country = l
                        break
                    except KeyError:
                        continue

        if job_title is not None:
            qualification_level = qualification_from_title(job_title)

        if job_link is not None:
            job_link = self.BASE_URL + job_link

        if company_link is not None:
            company_link = self.BASE_URL + company_link

        if work_schedule is not None:
            if work_schedule == "Full Time":
                work_schedule = "full-time"
            if work_schedule == "Part Time":
                work_schedule = "part-time"

        post_date = \
            G(meta_block.xpath("span[@class='when relatize'" + \
                              "]/text()").extract(), 0)

        vacancy_item['source'] = self.SOURCE
        vacancy_item['title'] = remove_whitespaces(job_title)
        vacancy_item['link'] = job_link
        vacancy_item['work_schedule'] = work_schedule
        vacancy_item['date'] = post_date
        vacancy_item['qualification_level'] = qualification_level

        if job_title is not None:
            if re.search(r'remote|telecommu', job_title, re.I):
                vacancy_item['telecommunicate'] = True

        company_item['name'] = remove_whitespaces(company_name)
        company_item['country'] = country
        company_item['state'] = state
        company_item['city'] = city
        company_item['website'] = company_link

        return vacancy_item, company_item, job_link, company_link


    def parse(self, response):
        jobs_list = response.xpath("//div[@id='page']//div" + \
                                   "[@class='column main']/table/tr")
        if jobs_list:
            for job in jobs_list:
                vacancy_item, company_item, job_link, company_link = \
                    self.parse_in_list(job)
                yield scrapy.Request(job_link, \
                                     meta={'vacancy': vacancy_item, \
                                            'company': company_item}, \
                                     callback=self.get_details)
