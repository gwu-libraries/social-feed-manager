# Cycle through all the TwitterUsers we're tracking and fetch as many
# new items as possible. Attempt to backfill up to the limit twitter
# provides (currently 3200 statuses).  Obey timeline and rate limit laws
# like a good citizen.  For more info:
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
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max
from django.db.utils import IntegrityError

import tweepy

from ui.models import authenticated_api, dt_aware_from_created_at
from ui.models import TwitterUser, TwitterUserItem
from ui.models import TwitterUserTimelineJob, TwitterUserTimelineError
from ui.utils import set_wait_time

from ui.tasks import user_timeline_task


class Command(BaseCommand):
    help = 'fetch status updates from twitter user timelines'

    option_list = BaseCommand.option_list + (
        make_option('--user', action='store', dest='user',
                    default=None, help='Specific user to fetch'),
    )

    def handle(self, *args, **options):
        user_timeline_task.delay(args, options)
