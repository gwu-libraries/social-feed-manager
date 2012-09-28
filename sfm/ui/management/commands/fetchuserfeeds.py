from datetime import datetime
from time import mktime, time

import feedparser
import requests

from django.core.management.base import BaseCommand
from django.utils import timezone

from ui.models import TwitterUser, TwitterUserItem

class Command(BaseCommand):
    help = 'fetch feeds for twitter users'

    def handle(self, *args, **options):
        # for every TwitterUser, fetch their feeds
        # for every item in their feed, save if necessary
        for twitter_user in TwitterUser.objects.all():
            print '-=> fetching feed for %s' % twitter_user.name
            r = requests.get(twitter_user.feed_url)
            print 'rate limit class/limit/remaining: %s/%s/%s' % (
                    r.headers['x-ratelimit-class'],
                    r.headers['x-ratelimit-limit'],
                    r.headers['x-ratelimit-remaining'])
            reset_seconds = int(r.headers['x-ratelimit-reset']) - int(time())
            print 'rate limit resets in: %s minutes' % (reset_seconds / 60.0)
            feed = feedparser.parse(r.content)
            for entry in feed['entries']:
                dt = datetime.fromtimestamp(mktime(entry['published_parsed']))
                dt_aware = timezone.make_aware(dt, timezone.utc)
                item, created = TwitterUserItem.objects.get_or_create(
                        twitter_user=twitter_user, 
                        date_published=dt_aware,
                        twitter_url=entry['link'],
                        item_text=entry['title'], 
                        place=entry['twitter_place'],
                        source=entry['twitter_source'])
                if created:
                    print 'saved   %s' % item
                else:
                    print 'skipped %s' % item

