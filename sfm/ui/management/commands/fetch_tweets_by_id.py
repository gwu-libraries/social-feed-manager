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
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        errors_occurred = False
        for tweetidline in fin:
            try:
                status = api.get_status(id=tweetidline)
                json_value = json.dumps(status) + '\n\n'
                outstream.write(json_value)
            except tweepy.error.TweepError as e:
                content = 'Error: %s for the tweetid: %s' \
                          % (e, tweetidline) + '\n'
                flog.write(content)
                errors_occurred = True
        fin.close()
        flog.close()
        if options.get('outputfile', True):
            outstream.close()
        if errors_occurred:
            print 'Completed with errors. Please view the log file for details'
