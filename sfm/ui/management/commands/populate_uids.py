# Cycle through all the TwitterUsers we're tracking.  For each TwitterUser,
# if the uid==0 (default value, i.e. it hasn't been set yet), look the
# user up by name and populate the uid.
# TODO:  Obey timeline and rate limit laws
# like a good citizen.  For more info:
#
# see https://dev.twitter.com/docs/api/1.1/get/users/lookup
#   for explanation of get_user call
# see https://dev.twitter.com/docs/working-with-timelines
#   for explanation of max_id, since_id usage
# see also:
#   https://dev.twitter.com/docs/error-codes-responses
#   https://dev.twitter.com/docs/rate-limiting

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

import tweepy

from ui.models import authenticated_api
from ui.models import TwitterUser


class Command(BaseCommand):
    help = 'Fetch uids for twitter users by name, where uids ' \
           + 'are not populated.  Intended for migrating old ' \
           + 'databases prior to m2_001.'

    option_list = BaseCommand.option_list + (
        make_option('--user', dest='user',
                    default=None, help='Specific user to update'),
    )

    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        qs_tweeps = TwitterUser.objects.filter(is_active=True)
        if options.get('user', None):
            qs_tweeps = qs_tweeps.filter(name=options.get('user'))
        qs_tweeps = qs_tweeps.order_by('date_last_checked')
        for tweep in qs_tweeps:
            print 'user: %s' % tweep.name
            # check user status, update twitter user name if it has changed
            try:
                # only update if tweep.uid == 0, otherwise leave it alone
                if tweep.uid == 0:
                    user_status = api.get_user(screen_name=tweep.name)
                    tweep.uid = user_status['id']
                    tweep.save()
            except tweepy.error.TweepError as e:
                print 'Error: %s' % e
                #find a way to just go to the next tweep in the for loop
                continue
