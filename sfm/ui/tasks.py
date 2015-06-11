from __future__ import absolute_import
from celery import Celery
import sys
import codecs
from ui.utils import xls_tweets_workbook
import json
import time
from django.conf import settings
from ui.models import authenticated_api
from django.db.models import Max
from django.db.utils import IntegrityError
# from celery.decorators import periodic_task
from datetime import timedelta
import datetime
import tweepy
from ui.models import dt_aware_from_created_at
from ui.models import TwitterUserItem
from ui.models import TwitterUserTimelineError
from ui.utils import set_wait_time

app = Celery('sfm', backend='amqp', broker='amqp://')
# celery = Celery('sfm')
# celery.config_from_object('celeryconfig')
app.conf.update(
    CELERYBEAT_SCHEDULE = {
        'multiply-each-10-seconds': {
            'task': 'tasks.add',
            'schedule': datetime.timedelta(seconds=10),
            'args': (2,2)
        },
    },
)


@app.task
def add(x, y):
    return x + y


@app.task(bind=True, ignore_result=True)
def exportcsv_task(self, xls, qs, filename):
    writer_class = codecs.getwriter('utf-8')
    sys.stdout = writer_class(sys.stdout, 'replace')
    if xls:
        tworkbook = xls_tweets_workbook(qs, TwitterUserItem.csv_headers)
        tworkbook.save(filename)
    else:
        print '\t'.join(TwitterUserItem.csv_headers)
        for tui in qs:
            print '\t'.join(tui.csv)


@app.task(bind=True, ignore_result=True, queue='usertimeline', run_every=timedelta(seconds=60))
def user_timeline(self, option, job, qs_tweeps):
    for tweep in qs_tweeps:
        print 'user: %s' % tweep.name
        if tweep.uid == 0:
            skipmsg = 'uid has not been set yet - skipping this ' + \
                'user.  May need to run populate_uids if this ' + \
                'is an old database.'
            print skipmsg
            error = TwitterUserTimelineError(job=job, user=tweep,
                                             error=skipmsg)
            error.save()
            continue
        since_id = 1
        if tweep.items.count() > 0:
            max_dict = tweep.items.all().aggregate(Max('twitter_id'))
            since_id = max_dict['twitter_id__max']
        max_id = 0
        tweep.save()
        user_timeline_individual.delay(option, job, since_id, max_id, tweep)


@app.task(bind=True, ignore_result=True, queue='usertimelinei')
def user_timeline_individual(self, option, job, since_id, max_id, tweep):
    api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
    while True:
        time.sleep(set_wait_time(getattr(api, 'last_response', None)))
        job.save()
        stop = False
        try:
            print 'since: %s' % (since_id)
            if max_id:
                print 'max: %s' % max_id
                timeline = api.user_timeline(id=tweep.uid,
                                             since_id=since_id,
                                             max_id=max_id, count=200)
            else:
                timeline = api.user_timeline(id=tweep.uid, since_id=since_id,
                                             count=200)
        except tweepy.error.TweepError as e:
            print 'ERROR: %s' % e
            error = TwitterUserTimelineError(job=job, user=tweep, error=e)
            error.save()
            timeline = []
            break
        if len(timeline) == 0:
            stop = True
        new_status_count = 0
        for status in timeline:
            dt_aware = dt_aware_from_created_at(status['created_at'])
            try:
                item, created = TwitterUserItem.objects.get_or_create(
                    twitter_user=tweep,
                    twitter_id=status['id'],
                    date_published=dt_aware,
                    item_text=status['text'],
                    item_json=json.dumps(status),
                    place=status['place'] or '',
                    source=status['source'])
                if created:
                    max_id = item.twitter_id - 1
                    new_status_count += 1
                else:
                    print 'skip: id %s' % item.id
            except IntegrityError as ie:
                print 'ERROR: %s' % ie
                error = TwitterUserTimelineError(job=job, user=tweep, error=ie)
                error.save()
        print 'saved: %s item(s)' % new_status_count
        job.num_added += new_status_count
        if new_status_count < 150:
            print 'stop: < 150 new statuses'
            stop = True
        if max_id < since_id:
            # Got 'em all, stop for this user
            print 'stop: max_id < since_id'
            stop = True
        # Check response codes for issues
        response_status = api.last_response.status_code
        if response_status >= 400:
            print 'error:', api.last_response.getheader('status')
            error = TwitterUserTimelineError(job=job, user=tweep, error=e)
            error.save()
            stop = True
        if stop:
            break
