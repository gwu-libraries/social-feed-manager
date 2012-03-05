from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

import requests

class Command(BaseCommand):
    args = '<rule1 rule2 ...>'
    help = 'Delete one or more rules'
    option_list = BaseCommand.option_list + (
        make_option('--tag', action='store', type='string',
            dest='tag', default=''),
        )

    def handle(self, *args, **options):
        data = {'rules': []} 
        for arg in args:
            rule = {'value': arg}
            if options.get('tag', None):
                rule['tag'] = options['tag']
            data['rules'].append(rule)
        print 'going to delete:'
        print json.dumps(data)
        headers = {'content-type': 'application/json'}
        resp = requests.delete(settings.GNIP_TWITTER_NOTICES_RULES_URL,
            auth=(settings.GNIP_USER, settings.GNIP_PASSWORD),
            headers=headers,
            data=json.dumps(data))
        print 'response:', resp.status_code
        print 'response text:', resp.text
