from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

import tweepy
from tweepy.streaming import StreamListener

from ui.models import RotatingFile

class StdOutListener(StreamListener):

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

class Command(BaseCommand):
    help = 'Show or save the Twitter sample/spritzer feed'

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
        user = User.objects.get(username=settings.TWITTER_DEFAULT_USERNAME)
        sa = user.social_auth.all()[0]
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(sa.tokens['oauth_token'],sa.tokens['oauth_token_secret'])
        if options.get('save', True):
           listener = RotatingFile(filename_prefix='sample',
                   save_interval_seconds=options['interval'],
                   data_dir=options['dir'])
           stream = tweepy.Stream(auth, listener)
           stream.sample()
        else:
           listener = StdOutListener()
           stream = tweepy.Stream(auth, listener)
           StdOutListener(stream.sample())
