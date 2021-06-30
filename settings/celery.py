from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
#from settings import BROKER_URL_

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# django.setup()
# app = Celery('settings', backend='redis://micro-paydoshop.rxhwl1.0001.euw2.cache.amazonaws.com:6379', broker='redis://micro-paydoshop.rxhwl1.0001.euw2.cache.amazonaws.com:6379')
app = Celery('settings', backend='redis://127.0.0.1:6379/0', broker='redis://127.0.0.1:6379/0')
# app = Celery('project',broker='amqp://',backend='amqp://',)
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# New Command
# celery -A settings worker --loglevel=INFO