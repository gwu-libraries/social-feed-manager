# Cycle through all the TwitterUsers we're tracking and fetch
# as many new items as possible.  Limit fetches to users who haven't
# been updated for at least some minimum interval.  Attempt to backfill
# up to the limit twitter provides (currently 3200 statuses).  Obey
# timeline and rate limit laws like a good citizen.  For more info:
#
# see https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline
#   for explanation of user_timeline call
# see https://dev.twitter.com/docs/working-with-timelines
#   for explanation of max_id, since_id usage
# see also:
#   https://dev.twitter.com/docs/error-codes-responses
#   https://dev.twitter.com/docs/rate-limiting

import json
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

class Command(BaseCommand):
    help = 'fetch status updates from twitter user timelines'
    
    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        qs_twitter_users = TwitterUser.objects.filter(is_active=True)
        qs_twitter_users = qs_twitter_users.order_by('date_last_checked')
        for twitter_user in qs_twitter_users:
            # Do they have any statuses recorded?
            if twitter_user.items.count():
                max_dict = twitter_user.items.all().aggregate(Max('twitter_id'))
                since_id = max_dict['twitter_id__max']
            else:
                since_id = 1
            max_id = 0
            # update their record (auto_now) as we're checking it now
            twitter_user.save()
            while True:
                stop = False
                print 'user: %s' % twitter_user.name
                try:
                    if max_id:
                        print 'since: %s' % since_id
                        print 'max: %s' % max_id
                        timeline = api.user_timeline(screen_name=twitter_user.name,
                                since_id=since_id, max_id=max_id, count=200)
                    else:
                        print 'since: %s' % (since_id)
                        timeline = api.user_timeline(screen_name=twitter_user.name,
                                since_id=since_id, count=200)
                except tweepy.error.TweepError as e:
                    print 'ERROR: %s' % e
                    # stop processing this user immediately
                    break
                if len(timeline) == 0:
                    # Nothing new; stop for this user
                    stop = True
                new_status_count = 0
                for status in timeline:
                    # eg 'Mon Oct 15 20:15:12 +0000 2012'
                    dt_aware = dt_aware_from_created_at(status['created_at'])
                    try:
                        item, created = TwitterUserItem.objects.get_or_create(
                                twitter_user=twitter_user,
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
                try:
                    remaining = int(api.last_response.getheader('x-rate-limit-remaining'))
                    reset = int(api.last_response.getheader('x-rate-limit-reset'))
                    reset_seconds = reset - int(time.time())
                    print 'remaining: %s, rate limit resets in %s minutes' % \
                            (remaining, reset_seconds / 60.0)
                except:
                    print 'error: calculating rate limits'
                    reset_seconds = remaining = 1
                if response_status == 200:
                    if remaining > 1:
                        wait_time = WAIT_BUFFER_SECONDS + (reset_seconds / remaining)
                        # #22: saw some negative ratelimit-reset/wait_times
                        # so cushion around that too
                        if wait_time < WAIT_BUFFER_SECONDS:
                            wait_time += WAIT_BUFFER_SECONDS
                        print 'sleep: %s seconds' % wait_time
                        time.sleep(wait_time)
                    else:
                        print 'error: no API calls remaining this window.'
                        stop = True
                elif response_status >= 500:
                    print 'error:', api.last_response.getheader('status')
                    stop = True
                elif response_status >= 400:
                    print 'error::', \
                            api.last_response.getheader('status')
                    stop = True
                if stop:
                    break
