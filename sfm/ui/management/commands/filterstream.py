from optparse import make_option
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import smart_bytes

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
        make_option('--list', action='store_true', dest='list',
                    help='list all twitterfilters')
    )

    #The help message will display the [twitterfilterid] as an arg
    @classmethod
    def usage(self, *args):
        usage = 'Usage: ./manage.py filterstream [twitterfilterid] ' + \
                '[options]' + '\n' + '\n' + self.help
        return usage

    def handle(self, *args, **options):
        if options.get('list', True):
            twitter_filter = TwitterFilter.objects.order_by('-is_active')
            print 'Twitterfilter id  Status\n' \
                  '----------------  ------'
            for items in twitter_filter:
                if items.is_active is True:
                    print str(items.id).rjust(16) + '  Active'
                else:
                    print str(items.id).rjust(16) + '  Inactive'
        else:
            if len(args) < 1:
                raise CommandError("at least one argument is required:twitterfilter id")
            try:
                twitter_filter = TwitterFilter.objects.get(id=int(args[0]))
            except:
                raise CommandError("unable to load that TwitterFilter")
            if twitter_filter.is_active is False:
                raise CommandError("TwitterFilter is not active")
            #words to track
            words = []
            words.append(twitter_filter.words)
            #people to track, fetch uids for each
            people = twitter_filter.people.strip('').split(',')
            uids = []
            if twitter_filter.uids != '':
                uids_split = smart_bytes(twitter_filter.uids).split(',')
                for ids in range(0, len(uids_split)):
                    val = uids_split[ids].lstrip("[").strip(' ').rstrip("]")
                    uids.append(str(val))
            #locations to track
            loc = []
            if twitter_filter.locations != '':
                for l in twitter_filter.locations.split(','):
                    loc.append(float(l))
            if options.get('verbose', False):
                print 'track:', words
                print 'follow:', people
                print 'locations:', loc
            try:
                sa = twitter_filter.user.social_auth.all()[0]
                auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                           settings.TWITTER_CONSUMER_SECRET)
                auth.set_access_token(sa.tokens['oauth_token'],
                                      sa.tokens['oauth_token_secret'])
                filename_prefix = 'twitterfilter-%s' % args[0]
                if options.get('save', True):
                    listener = RotatingFile(
                        filename_prefix=filename_prefix,
                        save_interval_seconds=options['interval'],
                        data_dir=options['dir'])
                    stream = tweepy.Stream(auth, listener)
                    stream.filter(track=words, follow=uids,
                                  locations=loc)
                else:
                    listener = StdOutListener()
                    stream = tweepy.Stream(auth, listener)
                    StdOutListener(stream.filter(
                        track=words, follow=uids, locations=loc))
            except Exception, e:
                if options.get('verbose', False):
                    print 'Disconnected from twitter:', e
                    print traceback.print_exc()
