# Cycle through all the TwitterUsers we're tracking and update any
# screen names that have changed.
#
# see https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline
#   for explanation of user_timeline call
# see https://dev.twitter.com/docs/working-with-timelines
#   for explanation of max_id, since_id usage
# see also:
#   https://dev.twitter.com/docs/error-codes-responses
#   https://dev.twitter.com/docs/rate-limiting

import json
from optparse import make_option
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

import tweepy

from ui.models import authenticated_api
from ui.models import TwitterUser


class Command(BaseCommand):
    help = 'update any screen names that have changed'

    option_list = BaseCommand.option_list + (
        make_option('--user', action='store', dest='user',
                    default=None, help='Specific user to fetch'),
    )

    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        qs_tweeps = TwitterUser.objects.filter(is_active=True)
        if options.get('user', None):
            qs_tweeps = qs_tweeps.filter(name=options.get('user'))
        for tweep in qs_tweeps:
            print 'user: %s' % tweep.name
            # check user status, update twitter user name if it has changed
            if tweep.uid == 0:
                print 'uid has not been set yet - skipping.'
                continue
            try:
                user_status = api.get_user(id=tweep.uid)
                if user_status['screen_name'] != tweep.name:
                    print ' -- updating screen name to %s' % \
                        user_status['screen_name']
                    oldnames = json.loads(tweep.former_names)
                    oldnames[datetime.datetime.now().strftime('%c')] = \
                        tweep.name
                    tweep.former_names = json.dumps(oldnames)
                    tweep.name = user_status['screen_name']
                    #TODO: Is this save unnecessary, since it gets saved below?
                    tweep.save()
            except tweepy.error.TweepError as e:
                print 'Error: %s' % e
                #go to the next tweep in the for loop
                continue
