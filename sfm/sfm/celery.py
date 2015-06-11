from __future__ import absolute_import

import os

from celery import Celery
from kombu import Queue, Exchange

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfm.settings')

from django.conf import settings

app = Celery('sfm')

# instantiate Celery object
celery = Celery(include=['sfm.ui.tasks'])

# import celery config file
celery.config_from_object('celeryconfig')

if __name__ == '__main__':
    celery.start()

# Define dedicated celery Queues
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('usertimelinei', Exchange('usertimelinei'),
          routing_key='usertimelinei'),
    Queue('usertimeline', Exchange('usertimeline'),
          routing_key='usertimeline'),
)

# Define Celery Routes
CELERY_ROUTES = {
    'ui.tasks.user_timeline': {'queue': 'usertimeline',
                               'routing_key': 'usertimeline'},
    'ui.tasks.user_timeline_individual': {'queue': 'usertimelinei',
                                          'routing_key': 'usertimelinei'},
}

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
"""
from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'tasks.user_timeline',
        'schedule': timedelta(seconds=30),
        'args': (option, job, qs_tweeps)
    },
}

CELERY_TIMEZONE = 'UTC'
"""


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
