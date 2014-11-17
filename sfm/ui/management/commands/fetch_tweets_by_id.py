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
        make_option('--limit', action='store',
            default=None, help='Limit on the number of tweets to fetch.'),

    )

    def handle(self, *args, **options):
        if options['inputfile'] is None:
            print 'Please specify a valid input file using --inputfile'
            return

        infile = options['inputfile']
        fin = open(infile, 'r+')
        logfile = infile + '.log'
        flog = open(logfile, 'w')
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
            if len(tweet_ids) == 5:
                errors_occurred = self.fetch(tweet_ids, api, outstream, flog) or errors_occurred
                tweet_ids = []
        #Final fetch
        errors_occurred = self.fetch(tweet_ids, api, outstream, flog) or errors_occurred
        fin.close()
        flog.close()
        if options.get('outputfile', True):
            outstream.close()
        if errors_occurred:
            print 'Completed with errors. Please view the log file (%s) for details' % logfile

    def fetch(self, tweet_ids, api, outstream, flog):
        if tweet_ids:
            try:
                statuses = api.statuses_lookup(tweet_ids)
                for status in statuses:
                    json_value = json.dumps(status) + '\n\n'
                    outstream.write(json_value)
            except tweepy.error.TweepError as e:
                content = 'Error: %s for the tweetids: %s' \
                          % (e, tweet_ids) + '\n'
                flog.write(content)
                #Return true if errors occurred
                return True
        return False
