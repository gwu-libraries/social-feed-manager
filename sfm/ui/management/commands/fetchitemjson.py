import time

import requests

from django.core.management.base import BaseCommand

from ui.models import TwitterUserItem

# How many times should I retry after an error before bailing out?
RETRY_CYCLES_MAX = 5
RETRY_CYCLE_SECONDS = 60 * 5 # five minutes

# A little added cushion
WAIT_BUFFER_SECONDS = 2

class Command(BaseCommand):
    help = 'fetch json for twitter items'

    def handle(self, *args, **options):
        # for every TwitterUserItem with blank json
        # fetch its json and store it
        # go in reverse chron order
        # attend to rate limits
        qs = TwitterUserItem.objects.filter(item_json='')
        qs = qs.order_by('date_published')
        updates_remaining = qs.count()
        retry_cycles_used = 0
        print '%s item(s) to fetch' % updates_remaining
        for item in qs:
            print '-=> fetching json for %s' % item.twitter_url
            print '    using %s' % item.tweet_json_url
            try:
                r = requests.get(item.tweet_json_url)
                # see https://dev.twitter.com/docs/error-codes-responses
                # and https://dev.twitter.com/docs/rate-limiting
                if r.status_code == 200:
                    item.item_json = r.content
                    item.save()
                    updates_remaining -= 1
                    print 'updated %s' % item.twitter_url
                    print 'updates remaining: %s' % updates_remaining
                elif r.status_code >= 500:
                    print 'twitter api error: %s' % r.status_code
                    # back off and try again, to a point
                    retry_cycles_used += 1
                    if retry_cycles_used >= RETRY_CYCLES_MAX:
                        print 'max retry cycles. something wrong at twitter.'
                        break
                    else:
                        print 'retry cycle %s' % retry_cycles_used
                        time.sleep(RETRY_CYCLE_SECONDS)
                elif r.status_code >= 400:
                    print 'twitter api block: %s' % r.status_code
                print 'rate limit class/limit/remaining: %s/%s/%s' % (
                        r.headers['x-ratelimit-class'],
                        r.headers['x-ratelimit-limit'],
                        r.headers['x-ratelimit-remaining'])
                reset_seconds = int(r.headers['x-ratelimit-reset']) - int(time.time())
                print 'rate limit resets in %s minutes' % (reset_seconds / 60.0)
                remaining = int(r.headers['x-ratelimit-remaining'])
                if remaining > 1:
                    wait_time = WAIT_BUFFER_SECONDS + (reset_seconds / remaining)
                    # #22: saw some negative ratelimit-reset/wait_times
                    # so cushion around that too
                    if wait_time < WAIT_BUFFER_SECONDS:
                        wait_time = WAIT_BUFFER_SECONDS * 5
                    print 'sleeping %s seconds' % wait_time
                    time.sleep(wait_time)
                else:
                    print 'No API calls remaining this hour.'
                    break
            except Exception as e:
                print e
