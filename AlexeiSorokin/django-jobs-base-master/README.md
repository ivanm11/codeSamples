# Django jobs parser README

[![N|Core-tech](http://core-tech.ru/img/ctlogo.png)](http://core-tech.ru)

Collecting data about current django companies and vacancies from defined internet sources.

### Available spiders:
- djangojobssite (djangojobs.net/jobs)
- indeed (indeed.com/q-Django-jobs)
- stackoverflow (stackoverflow.com/jobs/developer-jobs-using-django) 
- technojobs (technojobs.co.uk/django-jobs)
- github (jobs.github.com/positions?description=django)
- mashable (jobs.mashable.com/jobs/results/keyword/django)
- flexjobs (flexjobs.com/search?search=django)

### Installation steps:
- sudo apt-get install python-dev libxml2-dev libxslt1-dev zlib1g-dev
- mkdir django-jobs && cd django-jobs
- virtualenv venv && source venv/bin/activate
- git clone https://alexxmagpie@git.coretech.io/alexxmagpie/django-jobs-base.git
- cd django-jobs-base
- pip install -r requirements.txt

> latest version of pip is required. Use 'pip install --upgrade pip' to upgrade it.

### Setup postgres database:
- psql -U postgres
- CREATE DATABASE <dbname>;
- CREATE USER <username> WITH PASSWORD '<password>';
- GRANT ALL PRIVILEGES ON DATABASE <dbname> TO <username>;
- insert username, password and dbname into django-jobs-base/djangojobs/local_settings.py

> check /etc/postgresql/9.3/main/pg_hba.conf configuration if scrapy will throw exceptions about writing processes

### Alembic setup and usage:
Alembic is used for database migrations inside scrapy project.  
- replace sqlalchemy.url value appropriate to yours inside alembic.ini file
- create new revision with 'alembic revision -m "your description"'
- add changes to generated migration in /alembic/version/migration_name.py
- use 'alembic upgrade head' to run migration

> automigrations is not recommended since alembic not always generate it properly

> command 'alembic upgrade' can be used directly on revision, instead of head

### Setup telegram notifications bot:
Uncomment default or put your own credentials into local_settings.py

### Enable celery worker:
Celery should be enabled at least for cleaning database from expired records in errors table.  
Use command below to start it:  
celery -B -A tasks worker --loglevel=info  
> we use RabbitMQ as broker for celery, so be sure that it has been installed:  
> sudo apt-get install rabbitmq-server

### Crawling on crontab using virtual environment:
Schedule time, replace PROJECT_FOLDER and SPIDER_NAME with required and put it in crontab -e:
- * * * * * source ~/PROJECT_FOLDER/venv/bin/activate && cd ~/PROJECT_FOLDER/djangojobs/ && scrapy crawl SPIDER_NAME

### Selenium and PhantomJS:
Selenium PhantomJS driver is used to parse sites where needed content renders with JS.  
One and only required thing is to have correct path to PhantomJS driver at djangojobs/settings.py below PHANTOM_JS_PATH name.  

> suitable to your system driver can be downloaded at:  
> http://phantomjs.org/download.html  

### Jupyter sql queries pretty rendering:
Run jupyter notebook with:
- jupyter notebook
In notebook type:
- %load_ext sql
- %%sql postgresql://USER:PASSW@HOST/DB_NAME  
and sql query below...  
More information can be found at:  
https://github.com/catherinedevlin/ipython-sql  

### Sentry integration:
Register new app at sentry.io and put SENTRY_DSN into local_settings.py to monitor scrapy errors in sentry interface.

### Tests
To run spiders/utils.py functions tests:  
- python -m unittest spiders/tests
