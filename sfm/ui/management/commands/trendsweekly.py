import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import tweepy

from ui.models import TrendWeekly

class Command(BaseCommand):
    help = 'Fetch and store weekly twitter trends'

    def handle(self, *args, **options):
        api = tweepy.API()
        weekly = api.trends_weekly()
        for date, trends in weekly['trends'].iteritems():
            print '\n-=-=-\n'
            print 'date:', date
            new_items = 0
            for trend in trends:
                # note: avoid nulls in events or promoted_content
                events = trend['events'] or ''
                promoted_content = trend['promoted_content'] or ''
                tw, created = TrendWeekly.objects.get_or_create(
                    date=date, events=events, name=trend['name'], 
                    query=trend['query'], promoted_content=promoted_content)
                if created:
                    new_items += 1
            print '%s new item(s)' % new_items
