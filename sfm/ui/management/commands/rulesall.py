from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

import requests

class Command(BaseCommand):
    help = 'Show all existing rules'

    def handle(self, *args, **options):
        resp = requests.get(settings.GNIP_TWITTER_NOTICES_RULES_URL,
            auth=(settings.GNIP_USER, settings.GNIP_PASSWORD))
        try:
            data = json.loads(resp.text)
            tags = {}
            print 'All rules:'
            for rule in data['rules']:
                tag = rule.get('tag', None)
                value = rule.get('value', '')
                if tag:
                    print 'value: %s (tag %s)' % (value, tag)
                    try:
                        tags[tag].append(value)
                    except:
                        tags[tag] = [value]
                else:
                    print 'value: %s' % value
            if tags:
                print '\n\nTags:'
                for tag in sorted(tags.keys()):
                    print 'tag: %s, values: %s' % (tag, tags[tag])
            else:
                print '\nNo tags.'
        except:
            print 'status code:', resp.status_code
