from datetime import timedelta

# CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# Broker settings.
BROKER_URL = 'amqp://'

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'amqp://'

# specify location of log files
CELERYD_LOG_FILE = "/social-feed-manager/sfm/logs/celery.log"

# List of modules to import when celery starts.
CELERY_IMPORTS = ('ui.tasks', )

# CELERY_ANNOTATIONS = {'tasks.nameoftask': {'rate_limit': '10/s'}}
CELERY_ANNOTATIONS = {'*': {'rate_limit': '10/s'}}

# Define Exchange type - Default is Direct
# CELERY_RESULT_EXCHANGE_TYPE = 'Topic'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'EST'
CELERY_ENABLE_UTC = True
CELERY_IGNORE_RESULT = False
CELERY_TASK_RESULT_EXPIRES = 10
CELERY_TRACK_STARTED = True
CELERYD_CONCURRENCY = 2
CELERYD_PREFETCH_MULTIPLIER = 4
CELERY_SEND_TASK_SENT_EVENT = False

# Use Cron instead of Celerybeat schedule
CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'tasks.add',
        'schedule': timedelta(seconds=30),
        'args': (16, 16)
    },
}

