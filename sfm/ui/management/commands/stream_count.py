from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import os
import sfm.settings as settings
import gzip
from ui.management.utils import parse_date, get_stream_basename, include_dir


class Command(BaseCommand):
    help = 'count the number of tweets collected from a stream'

    option_list = BaseCommand.option_list + (
        make_option('--name', action='store', default=None,
                    type='string', dest='name',
                    help='name of twitter filter (otherwise, sample stream)'),
        make_option('--start-date', action='store', default=None,
                    type='string', dest='start_date',
                    help='earliest date (YYYY-MM-DD) for export'),
        make_option('--end-date', action='store', default=None,
                    type='string', dest='end_date',
                    help='latest date (YYYY-MM-DD) for export'),
    )


    def handle(self, *args, **options):
        #Use name option otherwise stream
        stream_base_name = get_stream_basename(options['name'])
        stream_dir = os.path.join(settings.DATA_DIR, stream_base_name)

        #Parse dates
        start_date = parse_date(options['start_date'])
        end_date = parse_date(options['end_date'])

        #Make sure directory for stream exists.
        if not os.path.exists(stream_dir):
            raise CommandError("Cannot count since %s does not exist" % stream_dir)

        count = 0
        for root, dirs, files in os.walk(stream_dir):
            for tweet_dir in dirs:
                if not include_dir(os.path.join(root, tweet_dir), stream_dir, start_date, end_date):
                    dirs.remove(tweet_dir)
            for tweet_file in files:
                count += self.count_tweets(os.path.join(root, tweet_file))
        print count

    @staticmethod
    def count_tweets(filepath):
        with gzip.open(filepath, "rb") as gz_file:
            count = 0
            for line in gz_file:
                if line != "\n":
                    count += 1
        return count



