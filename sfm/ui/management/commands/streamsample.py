from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

import requests

class Command(BaseCommand):
    help = 'Show the Twitter sample/spritzer feed'

    def handle(self, *args, **options):
        resp = requests.get(settings.TWITTER_SAMPLE_URL,
            auth=(settings.TWITTER_USER, settings.TWITTER_PASSWORD))

        for line in resp.iter_lines():
            if line:
                print line

