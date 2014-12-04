from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from ui.management.utils import parse_date, get_stream_basename, include_dir
import os
import sfm.settings as settings
import gzip
import json
from ui.models import dt_aware_from_created_at
import codecs

class Command(BaseCommand):
    help = 'export data for a stream in csv or xls'

    @classmethod
    def usage(self, *args):
        usage = 'Usage: ./manage.py export_stream_csv [export-filepath] ' + \
                '[options]' + '\n' + self.help
        return usage

    option_list = BaseCommand.option_list + (
        make_option('--name', action='store', default=None,
                    type='string', dest='name',
                    help='name of twitter filter (otherwise, sample stream)'),
        make_option('--export-dir', action='store', default=None,
                    type='string', dest='export_dir',
                    help='export directory (otherwise, <data-directory>/twitterfilter-<id>-export or ' +
                         '<data-directory>/streamsample-export)'),
        make_option('--start-date', action='store', default=None,
                    type='string', dest='start_date',
                    help='earliest date (YYYY-MM-DD) for export'),
        make_option('--end-date', action='store', default=None,
                    type='string', dest='end_date',
                    help='latest date (YYYY-MM-DD) for export'),
        make_option('--merge', action='store_true',
                    dest='merge',
                    help='merge tweets into fewer files'),
        make_option('--merge-max', action='store', default=1000000,
                    type='int', dest='merge_max',
                    help='maximum number of tweets to put in a file (set to capacity of spreadsheet) or 0 for no max'),
        make_option('--sample-rate', action='store', default=1,
                    type='int', dest='sample_rate',
                    help='when merging, export a sample of tweets (1 out of every <sample rate> tweets)')
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

        #Create export dir
        if options['export_dir']:
            export_dir = options.get('export_dir')
        else:
            export_dir = "%s-export" % stream_dir
        print "Exporting to %s" % export_dir

        #Sample rate
        sample_rate = options['sample_rate']
        if sample_rate > 1:
            print "Sampling 1 of %s tweets" % sample_rate

        #If merging
        if options['merge']:
            merge_max = options['merge_max']
            export_file_count = 0
            merge_count = 0
            export_file = None
            try:
                for csv_tweet in self.csv_tweet_stream_generator(stream_dir, sample_rate=sample_rate):
                    #Open a new export file if this is the first tweet (export_file_count == 0)
                    #or if the file has reached max.
                    if (merge_max and merge_count == merge_max) or export_file_count == 0:
                        #Close a previous file
                        if export_file:
                            export_file.close()
                        export_file_count += 1
                        export_filepath = self.get_export_filepath(export_dir, stream_base_name, export_file_count)
                        print "Writing to %s" % export_filepath
                        export_file = codecs.open(export_filepath, mode="w", encoding="utf-8")
                        export_file.write(self.csv_headers())
                        merge_count = 0
                    export_file.write(csv_tweet)
                    merge_count += 1
            finally:
                if export_file and not export_file.closed:
                    export_file.close()

        else:
            #Otherwise, write using original file names
            for tweet_file in self.tweet_file_generator(stream_dir, start_date, end_date):
                #Replace stream_dir with export_dir
                export_filepath = os.path.join(export_dir, "%s.csv" % tweet_file[len(stream_dir)+1:-3])
                export_parent_dir = os.path.dirname(export_filepath)
                if not os.path.exists(export_parent_dir):
                    os.makedirs(export_parent_dir)
                print "Writing to %s" % export_filepath
                with codecs.open(export_filepath, mode="w", encoding="utf-8") as export_file:
                    export_file.write(self.csv_headers())
                    for csv_tweet in self.csv_tweets_from_file_generator(tweet_file):
                        export_file.write(csv_tweet)

    @staticmethod
    def get_export_filepath(export_dir, stream_base_name, export_file_count):
        return os.path.join(export_dir, "%s-%s.csv" % (stream_base_name, export_file_count))

    @staticmethod
    def tweet_file_generator(stream_dir, start_date=None, end_date=None):
        """
        A generator that returns the files for a stream.
        """
        for root, dirs, files in os.walk(stream_dir):
            for tweet_dir in dirs:
                if not include_dir(os.path.join(root, tweet_dir), stream_dir, start_date, end_date):
                    dirs.remove(tweet_dir)
            for tweet_file in files:
                yield os.path.join(root, tweet_file)

    @staticmethod
    def csv_tweets_from_file_generator(tweet_file):
        """
        A generator that returns the tweets from a file.
        """
        with gzip.open(tweet_file, "rb") as gz_file:
            for line in gz_file:
                if line != "\n":
                    try:
                        tweet = json.loads(unicode(line))
                        yield unicode("\t".join(Command.csv(tweet)) + "\n")
                    except Exception:
                        #Malformed tweet. It happens.
                        continue

    @staticmethod
    def csv_tweet_stream_generator(stream_dir, sample_rate=1):
        """
        A generator that returns the tweets for a stream, optionally sampling.
        """
        sample_count = 0
        for tweet_file in Command.tweet_file_generator(stream_dir):
            for csv_tweet in Command.csv_tweets_from_file_generator(tweet_file):
                sample_count += 1
                if sample_count == sample_rate:
                    yield csv_tweet
                    sample_count = 0
#

    @staticmethod
    def csv_headers():
        return "\t".join(['created_at', 'created_at_date', 'twitter_id',
                          'screen_name', 'followers_count', 'friends_count',
                          'retweet_count', 'hashtags', 'in_reply_to_screen_name',
                          'mentions', 'twitter_url', 'is_retweet_strict',
                          'is_retweet', 'text', 'url1', 'url1_expanded', 'url2',
                          'url2_expanded']) + "\n"

    @staticmethod
    def csv(tweet):
        """
        A list of fields to include in csv. This is almost the same list as TwitterUserItem.csv
        """
        date_published = dt_aware_from_created_at(tweet['created_at'])
        r = [date_published.strftime(date_published, '%Y-%m-%dT%H:%M:%SZ'),
             date_published.strftime(date_published, '%m/%d/%Y'),
             tweet['id_str'],
             tweet['user']['screen_name'],
             str(tweet['user']['followers_count']),
             str(tweet['user']['friends_count']),
             str(tweet['retweet_count']),
             ', '.join([ht['text']
                        for ht in tweet['entities']['hashtags']]),
             tweet['in_reply_to_screen_name'] or '',
             ', '.join(["@" + m["screen_name"] for m in tweet["entities"]["user_mentions"]]),
             'http://twitter.com/%s/status/%s' % (tweet['user']['screen_name'], tweet['id_str']),
             str(Command.is_retweet(tweet)),
             str(Command.is_retweet(tweet, strict=False)),
             tweet['text'].replace('\n', ' '),
             ]
        # only show up to two urls w/expansions
        for url in tweet['entities']['urls'][:2]:
            r.extend([url['url'], url['expanded_url']])
        return r

    @staticmethod
    def is_retweet(tweet, strict=True):
        """A simple-minded attempt to catch RTs that aren't flagged
        by twitter proper with a retweeted_status.  This will catch
        some cases, others will slip through, e.g. quoted RTs in
        responses, or "RT this please".  Can't get them all. Likely
        heavily biased toward english."""
        if tweet.get('retweeted_status', False):
            return True
        if not strict:
            text_lower = tweet['text'].lower()
            if text_lower.startswith('rt '):
                return True
            if ' rt ' in text_lower:
                if not 'please rt' in text_lower \
                    and not 'pls rt' in text_lower \
                        and not 'plz rt' in text_lower:
                    return True
        return False
