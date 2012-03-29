from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

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
            # not sure if they're meaningfully ordered, but just in case
            sequence_num = 1
            for trend in trends:
                # note: avoid nulls in events or promoted_content
                events = trend['events'] or ''
                promoted_content = trend['promoted_content'] or ''
                tw, created = TrendWeekly.objects.get_or_create(
                    date=date, events=events, name=trend['name'], 
                    query=trend['query'], promoted_content=promoted_content,
                    sequence_num=sequence_num)
                if created:
                    print 'saved:', trend['name']
                sequence_num += 1
