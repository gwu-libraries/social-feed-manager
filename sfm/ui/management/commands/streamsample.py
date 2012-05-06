import gzip
from optparse import make_option
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

import requests

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

    def _get_filename(self):
        return '%s/sample-%s.xml.gz' % (settings.DATA_DIR,
            time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))

    def handle(self, *args, **options):
        resp = requests.get(settings.TWITTER_SAMPLE_URL,
            auth=(settings.TWITTER_USERNAME, settings.TWITTER_PASSWORD))
        if options.get('save', False):
            start_time = time.time()
            fp = gzip.open(self._get_filename(), 'wb')
            for line in resp.iter_lines():
                if line:
                    fp.write('%s\n' % line)
                    time_now = time.time()
                    if time_now - start_time > options['interval']:
                        fp.close()
                        fp = gzip.open(self._get_filename(), 'wb')
                        start_time = time_now
        else:
            for line in resp.iter_lines():
                if line:
                    print line


