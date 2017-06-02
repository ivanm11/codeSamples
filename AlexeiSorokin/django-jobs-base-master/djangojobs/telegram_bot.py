import sys
from settings import BASE_DIR, TELEGRAM, DOMAIN_NAME
sys.path.append(BASE_DIR)

import telegram

from djangojobs.models import Company, Vacancy
from djangojobs.pipelines import QueriesBase
from djangojobs.spiders.utils import DjangojobsError


class DjangoJobsTelegramNotifications(QueriesBase):
    """
    Telegram bot notifications about new database updates.
    """
    COMPANY_COUNT = None
    VACANCY_COUNT = None

    def __init__(self, spider):
        try:
            self.bot = telegram.Bot(token=TELEGRAM['BOT_TOKEN'])
        except Exception:
            raise DjangojobsError('Invalid or nonexistent telegram bot' + \
                                  'token. Check your local_settings.py.')

        try:
            chat = self.bot.get_chat(chat_id=TELEGRAM['CHAT_ID'])
        except Exception:
            raise DjangojobsError('Invalid or nonexistent telegram ' + \
                                 'chat id. Check your local_settings.py.')

        if chat.title != TELEGRAM['CHAT_TITLE']:
            raise DjangojobsError('Invalid chat title. Check your' + \
                                 'local_settings.py')

        self.c_id = TELEGRAM['CHAT_ID']
        self.spider = spider
        super(DjangoJobsTelegramNotifications, self).__init__()

    def count_records(self):
        session = self.Session()
        self.VACANCY_COUNT = session.query(Vacancy).count()
        self.COMPANY_COUNT = session.query(Company).count()

    def _get_records_ids(self, amount, table_name):
        ids = []
        session = self.Session()

        if table_name == 'company':
            model = Company
        elif table_name == 'vacancy':
            model = Vacancy
        else:
            raise DjangojobsError('Undefined table name:' + \
                                  '{0}.'.format(table_name))

        objs = session.query(model).order_by(model.id).all()[-amount:]
        for obj in objs:
            ids.append(obj.id)
        return ids

    def _generate_link(self, ids, table_name):
        if table_name == 'company':
            keyword = 'companies'
        elif table_name == 'vacancy':
            keyword = 'vacancies'
        else:
            raise DjangojobsError('Undefined table name:' + \
                                  '{0}.'.format(table_name))

        link = DOMAIN_NAME + '/found-' + keyword + '/' + \
                str(ids[0]) + '-' + str(ids[-1])

        return link

    def compare_countings(self):
        new_vacancies, new_companies = (0,) * 2
        vacancy_before = self.VACANCY_COUNT
        company_before = self.COMPANY_COUNT

        self.count_records()

        if vacancy_before is not None and self.VACANCY_COUNT is not None:
            new_vacancies = self.VACANCY_COUNT - vacancy_before

        if company_before is not None and self.COMPANY_COUNT is not None:
            new_companies = self.COMPANY_COUNT - company_before

        self.send_notification(new_vacancies, new_companies)

    def send_notification(self, new_vacancies, new_companies):
        vacancy_link, company_link = (None,) * 2

        if new_vacancies != 0:
            vacancy_ids = self._get_records_ids(new_vacancies, 'vacancy')
            vacancy_link = self._generate_link(vacancy_ids, 'vacancy')
        if new_companies != 0:
            company_ids = self._get_records_ids(new_companies, 'company')
            company_link = self._generate_link(company_ids, 'company')

        bot_message = \
        'Found {0} new vacancies, {1} new companies, {2}.'\
                .format(new_vacancies, new_companies, self.spider)

        if vacancy_link is not None:
            bot_message = bot_message + '\n{0}'.format(vacancy_link)
        if company_link is not None:
            bot_message = bot_message + '\n{0}'.format(company_link)

        if any([new_vacancies, new_companies]) != 0:
            self.bot.send_message(chat_id=self.c_id, text=bot_message)

