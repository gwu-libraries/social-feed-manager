from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

import requests

class Command(BaseCommand):
    help = 'Show the active feed using the stream'

    def handle(self, *args, **options):
        resp = requests.post(settings.GNIP_TWITTER_NOTICES_STREAM_URL,
            auth=(settings.GNIP_USER, settings.GNIP_PASSWORD))

        for line in resp.iter_lines():
            if line:
                print line

