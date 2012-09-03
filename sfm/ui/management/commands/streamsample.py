from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

import requests

from ui.models import RotatingFile

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

    def handle(self, *args, **options):
        resp = requests.get(settings.TWITTER_SAMPLE_URL,
            auth=(settings.TWITTER_USERNAME, settings.TWITTER_PASSWORD))
        if options.get('save', False):
            rfp = RotatingFile(stream=resp, 
                    filename_prefix='sample',
                    save_interval_seconds=options['interval'],
                    data_dir=options['dir'])
            rfp.handle()
        else:
            for line in resp.iter_lines():
                if line:
                    print line


