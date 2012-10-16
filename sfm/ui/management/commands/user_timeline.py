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

from datetime import datetime
import time 

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max
from django.utils import timezone
from django.utils import simplejson as json

from ui.models import authenticated_api, TwitterUser, TwitterUserItem

# A little added cushion
WAIT_BUFFER_SECONDS = 2

class Command(BaseCommand):
    help = 'fetch status updates from twitter user timelines'

    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        qs_twitter_users = TwitterUser.objects.order_by('-date_last_checked')
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
                print 'getting latest for user:', twitter_user.name
                if max_id:
                    print 'since_id %s, max_id %s' % (since_id, max_id)
                    timeline = api.user_timeline(screen_name=twitter_user.name,
                            since_id=since_id, max_id=max_id, count=200)
                else:
                    print 'since_id %s' % (since_id)
                    timeline = api.user_timeline(screen_name=twitter_user.name,
                            since_id=since_id, count=200)
                if len(timeline) == 0:
                    # Nothing new; stop for this user
                    break
                for status in timeline:
                    # eg 'Mon Oct 15 20:15:12 +0000 2012'
                    dt = datetime.fromtimestamp(time.mktime(time.strptime(status['created_at'], 
                            '%a %b %d %H:%M:%S +0000 %Y')))
                    dt_aware = timezone.make_aware(dt, timezone.utc)
                    item, created = TwitterUserItem.objects.get_or_create(
                            twitter_user=twitter_user,
                            twitter_id=status['id'],
                            date_published=dt_aware,
                            item_text=status['text'],
                            item_json=json.dumps(status),
                            place=status['place'] or '',
                            source=status['source'])
                    if created:
                        print 'saved twitter id %s' % item.twitter_id
                        max_id = item.twitter_id - 1
                    else:
                        print 'skipped id %s' % item.id
                if max_id < since_id:
                    # Got 'em all, stop for this user
                    print 'max_id < since_id'
                    break
                # Check response codes for issues
                response_status = api.last_response.status
                try:
                    remaining = int(api.last_response.getheader('x-rate-limit-remaining'))
                    reset = int(api.last_response.getheader('x-rate-limit-reset'))
                    reset_seconds = reset - int(time.time())
                    print 'remaining: %s, rate limit resets in %s minutes' % \
                            (remaining, reset_seconds / 60.0)
                except:
                    print 'error calculating rate limits'
                    reset_seconds = remaining = 1
                if response_status == 200:
                    if remaining > 1:
                        wait_time = WAIT_BUFFER_SECONDS + (reset_seconds / remaining)
                        # #22: saw some negative ratelimit-reset/wait_times
                        # so cushion around that too
                        if wait_time < WAIT_BUFFER_SECONDS:
                            wait_time += WAIT_BUFFER_SECONDS
                        print 'sleeping %s seconds' % wait_time
                        time.sleep(wait_time)
                    else:
                        print 'no API calls remaining this window.'
                        break
                elif response_status >= 500:
                    print 'API error:', api.last_response.getheader('status')
                    break
                elif response_status >= 400:
                    print 'API authorization issue:', \
                            api.last_response.getheader('status')
                    break
