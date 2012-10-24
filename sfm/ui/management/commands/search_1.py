from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from ui.models import authenticated_api

class Command(BaseCommand):
    help = 'perform a simple search against v1 search api'

    option_list = BaseCommand.option_list + (
        make_option('--since_id', action='store', type='int',
            default=0, dest='since_id',
            help='limit to tweets after this id'),
        )

    def handle(self, *args, **options):
        api = authenticated_api(settings.TWITTER_DEFAULT_USERNAME,
            api_root='/1')
        since_id = options['since_id']
        s = api.search(args[0], rpp=100, since_id=since_id)
        while True:
            if not s['results']:
                break
            for r in s['results']:
                print r
            s = api.search(args[0], rpp=100, max_id=s['max_id'],
                page=s['page'] + 1)
