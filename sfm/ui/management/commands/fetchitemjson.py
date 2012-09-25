import time

import requests

from django.core.management.base import BaseCommand

from ui.models import TwitterUserItem

class Command(BaseCommand):
    help = 'fetch json for twitter items'

    def handle(self, *args, **options):
        # for every TwitterUserItem with blank json
        # fetch its json and store it
        # go in reverse chron order
        # attend to rate limits
        qs = TwitterUserItem.objects.filter(item_json='')
        qs = qs.order_by('date_published')
        for item in qs:
            print '-=> fetching json for %s' % item.twitter_url
            print '    using %s' % item.tweet_json_url
            try:
                r = requests.get(item.tweet_json_url)
                print 'rate limit class/limit/remaining: %s/%s/%s' % (
                        r.headers['x-ratelimit-class'],
                        r.headers['x-ratelimit-limit'],
                        r.headers['x-ratelimit-remaining'])
                reset_seconds = int(r.headers['x-ratelimit-reset']) - int(time.time())
                remaining = int(r.headers['x-ratelimit-remaining'])
                print 'rate limit resets in %s minutes' % (reset_seconds / 60.0)
                item.item_json = r.content
                item.save()
                print 'updated %s' % item.twitter_url
                if remaining > 1:
                    wait_time = reset_seconds / remaining
                    print 'sleeping %s seconds' % wait_time
                    time.sleep(wait_time)
                else:
                    print 'No API calls remaining this hour.'
                    break
            except Exception as e:
                print e
