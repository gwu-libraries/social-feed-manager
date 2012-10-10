from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

import tweetstream

from ui.models import RotatingFile, Rule


class Command(BaseCommand):
    help = 'Filter tweets based on active rules'

    option_list = BaseCommand.option_list + (
        make_option('--save', action='store_true', default=False,
            dest='save', help='save the data to disk'),
        make_option('--dir', action='store', type='string',
            default=settings.DATA_DIR, dest='dir',
            help='directory for storing the data (default=%s)' % settings.DATA_DIR),
        make_option('--interval', action='store', type='int',
            default=settings.SAVE_INTERVAL_SECONDS, dest='interval',
            help='how often to save data (default=%s)' % settings.SAVE_INTERVAL_SECONDS),
        )

    def handle(self, *args, **options):
        rules = Rule.objects.filter(is_active=True)
        if not rules:
            print 'no rules to filter on'
            return
        words = set()
        people = set()
        locations = set()
        for rule in rules:
            words.update(rule.words.split(' ') if rule.words else [])
            people.update(rule.people.split(' ') if rule.people else [])
            locations.update(rule.locations.split(' ') if rule.locations else [])
        try:
            stream = tweetstream.FilterStream(settings.TWITTER_USERNAME,
                    settings.TWITTER_PASSWORD, track=words, 
                    follow=people, locations=locations)
            if options.get('save', False):
                rfp = RotatingFile(stream=stream, 
                        filename_prefix='filter',
                        save_interval_seconds=options['interval'],
                        data_dir=options['dir'])
                rfp.handle()
            else:
                for line in stream:
                    if line:
                        print line
        except tweetstream.ConnectionError, e:
            print 'Disconnected from twitter:', e.reason
