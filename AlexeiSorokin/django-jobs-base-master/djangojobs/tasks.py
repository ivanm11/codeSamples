import sys
from settings import BASE_DIR
sys.path.append(BASE_DIR)

import datetime

from celery import Celery
from celery.decorators import periodic_task
from celery.schedules import crontab
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from djangojobs.models import Errors
from djangojobs.pipelines import QueriesBase
from djangojobs.spiders.djangojobssite import DjangojobssiteSpider
from djangojobs.spiders.github import GithubSpider
from djangojobs.spiders.indeed import IndeedSpider
from djangojobs.spiders.mashable import MashableSpider
from djangojobs.spiders.stackoverflow import StackoverflowSpider
from djangojobs.spiders.technojobs import TechnojobsSpider
from djangojobs.spiders.flexjobs import FlexjobsSpider
from djangojobs.spiders.utils import DjangojobsError


app = Celery('djangojobs', broker='pyamqp://guest@localhost//')


class ExtractQueriesBase(QueriesBase):
    def __init__(self):
        super(ExtractQueriesBase, self).__init__()

    def extract(self):
        return self.Session()


#@app.on_after_configure.connect
#def setup_periodic_task(sender, **kwargs):
#    sender.add_periodic_task(
#        crontab(hour=0, minute=0),
#        clear_errors_table(),
#    )
#
#    sender.add_periodic_task(
#        crontab(hour=0, minute=10),
#        run_spiders(),
#    )


@periodic_task(run_every=datetime.timedelta(hours=48))
def clear_errors_table():
    """
    Removes records from Errors table older than 48 hours.
    """
    session = ExtractQueriesBase().extract()
    timedelta = datetime.datetime.now() - datetime.timedelta(hours=48)
    session.query(Errors).filter(Errors.error_datetime < \
                                            timedelta).delete()
    session.commit()
    return


@periodic_task(run_every=datetime.timedelta(hours=25))
def run_spiders():
    """
    Starts djangojobs spiders.
    """
    process = CrawlerProcess(get_project_settings())

    process.crawl(DjangojobssiteSpider)
    process.crawl(GithubSpider)
    process.crawl(IndeedSpider)
    process.crawl(MashableSpider)
    process.crawl(StackoverflowSpider)
    process.crawl(TechnojobsSpider)
    process.crawl(FlexjobsSpider)
    process.start()

    return

