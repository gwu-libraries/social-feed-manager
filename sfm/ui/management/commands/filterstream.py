from optparse import make_option
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

import tweepy
from tweepy.streaming import StreamListener

from ui.models import RotatingFile, Rule

class RotatingFileListener(StreamListener):

    def __init__(self, rf):
        self._rf = rf

    def on_data(self, data):
        pass

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
            gelmanbot = User.objects.get(username='gelmanbot')
            sa = gelmanbot.social_auth.all()[0]
            auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, 
                    settings.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(sa.tokens['oauth_token'], 
                    sa.tokens['oauth_token_secret'])
            listener = RotatingFile(filename_prefix='filter',
                    save_interval_seconds=options['interval'],
                    data_dir=options['dir'])
            stream = tweepy.Stream(auth, listener)
            stream.filter(track=words)
            if options.get('save', False):
                for line in stream:
                    if line:
                        print line
        except Exception, e:
            print 'Disconnected from twitter:', e
            print traceback.print_exc()
