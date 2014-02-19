from optparse import make_option
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

import tweepy
from tweepy.streaming import StreamListener

from ui.models import RotatingFile, TwitterFilter


# NOTE: "filter" is both a python built-in function and the name of
# the twitter api / tweepy function we are invoking, so we use the
# variable name "twitter_filter" throughout to avoid possible confusion
# http://docs.python.org/2/library/functions.html#filter


class StdOutListener(StreamListener):

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


class Command(BaseCommand):
    help = 'Filter tweets based on active filters'

    option_list = BaseCommand.option_list + (
        make_option('--save', action='store_true', default=False,
                    dest='save', help='save the data to disk'),
        make_option('--verbose', action='store_true', default=False,
                    dest='verbose', help='print debugging info to stdout'),
        make_option('--dir', action='store', type='string',
                    default=settings.DATA_DIR, dest='dir',
                    help='directory for storing the data (default=%s)'
                    % settings.DATA_DIR),
        make_option('--interval', action='store', type='int',
                    default=settings.SAVE_INTERVAL_SECONDS, dest='interval',
                    help='how often to save data (default=%s)'
                    % settings.SAVE_INTERVAL_SECONDS),
        make_option('--tfilterid', action='store', dest='tfilterid',
                    default=None, help='specify the twitter filter id')
    )

    def handle(self, *args, **options):
        twitter_filters = TwitterFilter.objects.filter(is_active=True)
        if not twitter_filters:
            if options.get('verbose', False):
                print 'no twitter_filters to filter on'
            return
        words = set()
        people = set()
        locations = set()
        for twitter_filter in twitter_filters:
            words.update(twitter_filter.words.strip().split(' ')
                         if twitter_filter.words else [])
            people.update(twitter_filter.people.strip().split(' ')
                          if twitter_filter.people else [])
            locations.update(twitter_filter.locations.strip().split(' ')
                             if twitter_filter.locations else [])
        if options.get('verbose', False):
            print 'track:', words
            print 'follow:', people
            print 'locations:', locations

        try:
            user = User.objects.get(username=settings.TWITTER_DEFAULT_USERNAME)
            sa = user.social_auth.all()[0]
            auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                       settings.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(sa.tokens['oauth_token'],
                                  sa.tokens['oauth_token_secret'])
            if options.get('tfilterid', None):
                twitter_filters = twitter_filters.filter(
                    id=options.get('tfilterid'))
                for rules in twitter_filters:
                    if rules.is_active is True and options.get('save', True):
                        listener = RotatingFile(
                            filename_prefix='filter',
                            save_interval_seconds=options['interval'],
                            data_dir=options['dir'])
                        stream = tweepy.Stream(auth, listener)
                        stream.filter(
                            track=words, follow=people, locations=locations)
                    else:
                        listener = StdOutListener()
                        stream = tweepy.Stream(auth, listener)
                        StdOutListener(stream.filter(
                            track=words, follow=people, locations=locations))
            if options.get('save', True):
                listener = RotatingFile(
                    filename_prefix='filter',
                    save_interval_seconds=options['interval'],
                    data_dir=options['dir'])
                stream = tweepy.Stream(auth, listener)
                stream.filter(track=words, follow=people, locations=locations)
            else:
                listener = StdOutListener()
                stream = tweepy.Stream(auth, listener)
                StdOutListener(stream.filter(
                    track=words, follow=people, locations=locations))
        except Exception, e:
            if options.get('verbose', False):
                print 'Disconnected from twitter:', e
                print traceback.print_exc()
