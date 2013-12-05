# Cycle through all the TwitterUsers we're tracking and fetch as many
# new items as possible. Attempt to backfill up to the limit twitter
# provides (currently 3200 statuses).  Obey timeline and rate limit laws
# like a good citizen.  For more info:
#
# see https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline
#   for explanation of user_timeline call
# see https://dev.twitter.com/docs/working-with-timelines
#   for explanation of max_id, since_id usage
# see also:
#   https://dev.twitter.com/docs/error-codes-responses
#   https://dev.twitter.com/docs/rate-limiting

import json
from optparse import make_option
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max
from django.db.utils import IntegrityError

import tweepy

from ui.models import authenticated_api, dt_aware_from_created_at
from ui.models import TwitterUser, TwitterUserItem

# A little added cushion
WAIT_BUFFER_SECONDS = 2


def set_wait_time(last_response):
    """based on last tweepy api response, calculate a time buffer in
    seconds to wait before issuing next api call."""
    wait_time = 0
    try:
        remaining = int(last_response.getheader('x-rate-limit-remaining'))
        reset = int(last_response.getheader('x-rate-limit-reset'))
        reset_seconds = reset - int(time.time())
    except:
        remaining = reset_seconds = 1
    # the out-of-calls-for-this-window case
    if remaining == 0:
        return reset_seconds + WAIT_BUFFER_SECONDS
    else:
        wait_time = (reset_seconds / remaining) + WAIT_BUFFER_SECONDS
    # #22: saw some negative ratelimit-reset/wait_times
    # so cushion around that too
    while wait_time < WAIT_BUFFER_SECONDS:
        wait_time += WAIT_BUFFER_SECONDS
    return wait_time


class Command(BaseCommand):
    help = 'fetch status updates from twitter user timelines'

    option_list = BaseCommand.option_list + (
        make_option('--user', action='store', dest='user',
                    default=None, help='Specific user to fetch'),
    )

    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        qs_tweeps = TwitterUser.objects.filter(is_active=True)
        if options.get('user', None):
            qs_tweeps = qs_tweeps.filter(name=options.get('user'))
        qs_tweeps = qs_tweeps.order_by('date_last_checked')
        for tweep in qs_tweeps:
            print 'user: %s' % tweep.name
            since_id = 1
            # set since_id if they have any statuses recorded
            if tweep.items.count() > 0:
                max_dict = tweep.items.all().aggregate(Max('twitter_id'))
                since_id = max_dict['twitter_id__max']
            max_id = 0
            # update their record (auto_now) as we're checking it now
            tweep.save()
            while True:
                stop = False
                try:
                    print 'since: %s' % (since_id)
                    if max_id:
                        print 'max: %s' % max_id
                        timeline = api.user_timeline(screen_name=tweep.name,
                                                     since_id=since_id,
                                                     max_id=max_id, count=200)
                    else:
                        timeline = api.user_timeline(screen_name=tweep.name,
                                                     since_id=since_id,
                                                     count=200)
                except tweepy.error.TweepError as e:
                    print 'ERROR: %s' % e
                    timeline = []
                if len(timeline) == 0:
                    # Nothing new; stop for this user
                    stop = True
                new_status_count = 0
                for status in timeline:
                    # eg 'Mon Oct 15 20:15:12 +0000 2012'
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
                print 'saved: %s item(s)' % new_status_count
                # max new statuses per call is 200, so check for less than
                # a reasonable fraction of that to see if we should stop
                if new_status_count < 150:
                    print 'stop: < 150 new statuses'
                    stop = True
                if max_id < since_id:
                    # Got 'em all, stop for this user
                    print 'stop: max_id < since_id'
                    stop = True
                # Check response codes for issues
                response_status = api.last_response.status
                if response_status >= 400:
                    print 'error:', api.last_response.getheader('status')
                    stop = True
                # wait before next call no matter what
                time.sleep(set_wait_time(api.last_response))
                if stop:
                    break
