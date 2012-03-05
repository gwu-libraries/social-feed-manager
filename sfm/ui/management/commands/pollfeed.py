import gzip
from optparse import make_option
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import requests

class Command(BaseCommand):
    help = 'Poll for data from the feed, optionally saving'
    option_list = BaseCommand.option_list + (
        make_option('--save', action='store_true', default=False,
            dest='save', help='save the data to disk'),
        make_option('--dir', action='store', type='string',
            default=settings.DATA_DIR, dest='dir', 
            help='directory for storing the data (default=DATA_DIR'),
        make_option('--interval', action='store', type='int',
            default=settings.SAVE_INTERVAL_SECONDS, dest='interval', 
            help='how often to save data (default=300)'),
        make_option('--max', action='store', type='string',
            default='100', dest='max', 
            help='max entries to poll for'),
        make_option('--since_date', action='store', dest='since_date',
            help='return activities since YYYYmmddHHMMSS (UTC)'),
        make_option('--to_date', action='store', dest='to_date',
            help='return activities before YYYYmmddHHMMSS (UTC)'),
        )

    def handle(self, *args, **options):
        data = {}
        for param in ['max', 'since_date', 'to_date']:
            if options.get(param, None):
                data[param] = options[param]
        resp = requests.get(settings.GNIP_TWITTER_NOTICES_STREAM_URL,
            auth=(settings.GNIP_USER, settings.GNIP_PASSWORD),
            params=data)

        entry = []
        if options.get('save', False):
            start_time = time.time()
            fp = gzip.open(self._get_filename(), 'wb')
            for line in resp.iter_lines():
                if line:
                    entry.append(line)
                    if '</entry>' in line:
                        fp.write('\n'.join(entry) + '\n')
                        entry = []
                        time_now = time.time()
                        if time_now - start_time > options['interval']:
                            fp.close()
                            fp = gzip.open(self._get_filename(), 'wb')
                            start_time = time_now
        else:
            for line in resp.iter_lines():
                if line:
                    print line
                    

    def _get_filename(self):
        return '%s/poll-%s.xml.gz' % (settings.DATA_DIR, 
            time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
