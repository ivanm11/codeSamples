# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os, sys

from datetime import datetime
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver

from djangojobs.settings import ERROR_LOGS
from models import Errors
from settings import PHANTOM_JS_PATH
from statistic import QueriesBase
from telegram_bot import DjangoJobsTelegramNotifications


class DjangoJobsErrorCollector(QueriesBase):
    """
    Saving exceptions raised during crawling into database.
    """
    def __init__(self, response, exception, spider):
        self.response = response
        self.exception = exception
        self.spider = spider
        super(DjangoJobsErrorCollector, self).__init__()

    def error_collector(self):
        session = self.Session()
        now = datetime.now()
        exc_type, exc_obj, exc_tb = sys.exc_info()
        last_exc_tb = exc_tb.tb_next

        while True is True:
            if last_exc_tb.tb_next is not None:
                last_exc_tb = last_exc_tb.tb_next
            else:
                break

        fname = os.path.split(last_exc_tb.tb_frame.f_code.co_filename)[1]
        lineno = last_exc_tb.tb_lineno
        exc_name = self.exception.__class__.__name__
        exc_message = self.exception.message
        source = self.spider.SOURCE

        error = Errors(vacancy_link=self.response.url, \
                       source=source, \
                       file_name=fname, \
                       error_type=exc_name, \
                       error_message=exc_message, \
                       error_lineno=lineno, \
                       error_datetime=now)

        session.add(error)
        session.commit()

        return self.response.url, source, fname, exc_name, \
                exc_message, lineno, now


class DjangojobsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    def __init__(self, crawler):
        crawler.signals.connect(self.close_spider, signals.spider_closed)
        crawler.signals.connect(self.open_spider, signals.spider_opened)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(crawler)

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        vacancy_link, source, file_name, error_type, \
            error_message, error_lineno, error_datetime = \
                DjangoJobsErrorCollector(response, exception, \
                                         spider).error_collector()

        error_datetime = error_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.output_file.write(source + ',' + \
                                error_datetime + ',' + \
                               vacancy_link + ',' + \
                               error_type + ',' + \
                               error_message + ',' + \
                               str(error_lineno) + ',' + \
                               '\n')

        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def open_spider(self, spider):
        self.output_file = open(ERROR_LOGS, 'a')
        self.notifications_obj = DjangoJobsTelegramNotifications(spider.SOURCE)
        self.notifications_obj.count_records()

    def close_spider(self, spider):
        self.output_file.close()
        self.notifications_obj.compare_countings()


class JSMiddleware(object):
    def process_request(self, request, spider):
        driver = webdriver.PhantomJS(executable_path=PHANTOM_JS_PATH)
        driver.get(request.url)

        body = driver.page_source
        return HtmlResponse(driver.current_url, body=body, encoding='utf-8',
                            request=request)

