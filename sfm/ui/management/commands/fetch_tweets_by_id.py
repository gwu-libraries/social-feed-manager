import json
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

import tweepy
import sys
from ui.models import authenticated_api


class Command(BaseCommand):
    help = 'Fetch tweet data as JSON for a list of tweet ids' \

    option_list = BaseCommand.option_list + (
        make_option('--inputfile', action='store',
                    default=None, help='Path of the input file containing \
                            a list of tweet ids, each on a separate line'),
        make_option('--outputfile', action='store',
                    default=None, help='Path of the output file'),
        make_option('--lognotfound', action='store_true',
                    default=False, help='Log a list of tweet ids that were \
                            not found, each on a separate line'),
        make_option('--limit', action='store',
                    default=None, help='Limit on the number of tweets to fetch.')

    )

    def handle(self, *args, **options):
        if options['inputfile'] is None:
            print 'Please specify a valid input file using --inputfile'
            return

        infile = options['inputfile']
        fin = open(infile, 'r+')
        if options['lognotfound']:
            logfile = options['inputfile'] + '.log'
            flog = open(logfile, 'w')
        else:
            flog = None
        if options['outputfile']:
            outfile = options['outputfile']
            outstream = open(outfile, 'w')
        else:
            outstream = sys.stdout
        limit = int(options['limit']) if options['limit'] else None
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        assert api
        errors_occurred = False
        tweet_ids = []
        for count, tweetidline in enumerate(fin):
            if limit and limit == count:
                print "Reached limit of %s tweets" % limit
                break
            tweet_ids.append(tweetidline[:-1])
            if len(tweet_ids) == 100:
                errors_occurred = self.fetch(tweet_ids, api, outstream, flog) or errors_occurred
                tweet_ids = []
        # Final fetch
        errors_occurred = self.fetch(tweet_ids, api, outstream, flog) or errors_occurred
        fin.close()
        if options.get('outputfile', True):
            outstream.close()
        if errors_occurred and options.get('logfile', True):
            print 'Some tweets not found. View the log file (%s) for ids of missing tweets' % logfile
            flog.close()

    def fetch(self, tweet_ids, api, outstream, flog):
        if tweet_ids and flog:
            tweets_orig = set(tweet_ids)
            found_ids = set()
            statuses = api.statuses_lookup(tweet_ids)
            for status in statuses:
                json_value = json.dumps(status) + '\n'
                outstream.write(json_value)
                found_ids.add(status['id_str'])
            missing_tweets = set(tweets_orig - found_ids)
            if len(missing_tweets) > 0:
                for m in missing_tweets:
                    flog.write(m + '\n')
                return True
            else:
                return False
        elif tweet_ids:
            statuses = api.statuses_lookup(tweet_ids)
            for status in statuses:
                json_value = json.dumps(status) + '\n'
                outstream.write(json_value)
            return False
