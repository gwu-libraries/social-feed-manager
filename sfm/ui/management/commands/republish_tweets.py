import json
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

import tweepy
from ui.models import authenticated_api


class Command(BaseCommand):
    help = 'fetch tweets respective to tweetid and' \
           'saves them into a output file'

    option_list = BaseCommand.option_list + (
        make_option('--infile', action='store',
                    dest='infile',
                    default=None, help='Specify the path of the input-file'),
        make_option('--outfile', action='store', dest='outfile',
                    default=None, help='Specify the path of the output file'),
    )

    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        if options.get('infile', True):
            infile = options['infile']
            fin = open(infile, 'r+')
            tweetid = fin.readlines()
            for i in range(len(tweetid)-1):
                try:
                    status = api.get_status(id=tweetid[i])
                    json_value = json.dumps(status) + '\n\n'
                    if options.get('outfile', True):
                        outfile = options['outfile']
                        fout = open(outfile, "a")
                        fout.write(json_value)
                        fout.close()
                    else:
                        print json_value
                except tweepy.error.TweepError as e:
                    if options.get('outfile', True):
                        logfile = outfile.replace('.txt', '.log')
                        flog = open(logfile, 'a')
                        content = 'Error: %s for the tweetid: %s' \
                                  % (e, tweetid[i]) + '\n'
                        flog.write(content)
                        flog.close()
                        print 'Error: Please view the log file for details'
                    else:
                        print 'Error: %s for the tweetid: %s' % (e, tweetid[i])
            fin.close()
