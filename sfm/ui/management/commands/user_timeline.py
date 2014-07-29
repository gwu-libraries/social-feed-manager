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


class Command(BaseCommand):
    help = 'fetch status updates from twitter user timelines'

    option_list = BaseCommand.option_list + (
        make_option('--user', action='store', dest='user',
                    default=None, help='Specific user to fetch'),
    )

    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        job = TwitterUserTimelineJob()
        job.save()
        qs_tweeps = TwitterUser.objects.filter(is_active=True)
        if options.get('user', None):
            qs_tweeps = qs_tweeps.filter(name=options.get('user'))
        else:
            # NOTE: randomizing here might be healthier when considering
            # possibility of multiple parallel jobs running and competing
            # for api calls but this is an instinctual call, not data-driven
            qs_tweeps = qs_tweeps.order_by('?')
        for tweep in qs_tweeps:
            print 'user: %s' % tweep.name
            # can't do this unless we have a twitter user_id stored
            if tweep.uid == 0:
                skipmsg = 'uid has not been set yet - skipping this ' + \
                          'user.  May need to run populate_uids if this ' + \
                          'is an old database.'
                print skipmsg
                error = TwitterUserTimelineError(job=job, user=tweep,
                                                 error=skipmsg)
                error.save()
                continue
            # now move on to determining first tweet id to get
            since_id = 1
            # set since_id if they have any statuses recorded
            if tweep.items.count() > 0:
                max_dict = tweep.items.all().aggregate(Max('twitter_id'))
                since_id = max_dict['twitter_id__max']
            max_id = 0
            # update their record (auto_now) as we're checking it now
            tweep.save()
            while True:
                # wait before next call no matter what;
                # use getattr() because api might be None the first time or
                # after errors
                time.sleep(set_wait_time(getattr(api, 'last_response', None)))
                job.save()
                stop = False
                try:
                    print 'since: %s' % (since_id)
                    if max_id:
                        print 'max: %s' % max_id
                        timeline = api.user_timeline(id=tweep.uid,
                                                     since_id=since_id,
                                                     max_id=max_id, count=200)
                    else:
                        timeline = api.user_timeline(id=tweep.uid,
                                                     since_id=since_id,
                                                     count=200)
                except tweepy.error.TweepError as e:
                    print 'ERROR: %s' % e
                    error = TwitterUserTimelineError(job=job, user=tweep,
                                                     error=e)
                    error.save()
                    timeline = []
                    break
                if len(timeline) == 0:
                    # Nothing new; stop for this user
                    stop = True
                new_status_count = 0
                for status in timeline:
                    # eg 'Mon Oct 15 20:15:12 +0000 2012'
                    dt_aware = dt_aware_from_created_at(status['created_at'])
                    try:
                        item, created = TwitterUserItem.objects.get_or_create(
                            twitter_user=tweep,
                            twitter_id=status['id'],
                            date_published=dt_aware,
                            item_text=status['text'],
                            item_json=json.dumps(status),
                            place=status['place'] or '',
                            source=status['source'])
                        if created:
                            max_id = item.twitter_id - 1
                            new_status_count += 1
                        else:
                            print 'skip: id %s' % item.id
                    except IntegrityError as ie:
                        print 'ERROR: %s' % ie
                        error = TwitterUserTimelineError(job=job, user=tweep,
                                                         error=ie)
                        error.save()
                print 'saved: %s item(s)' % new_status_count
                job.num_added += new_status_count
                # max new statuses per call is 200, so check for less than
                # a reasonable fraction of that to see if we should stop
                if new_status_count < 150:
                    print 'stop: < 150 new statuses'
                    stop = True
                if max_id < since_id:
                    # Got 'em all, stop for this user
                    print 'stop: max_id < since_id'
                    stop = True
                # Check response codes for issues
                response_status = api.last_response.status
                if response_status >= 400:
                    print 'error:', api.last_response.getheader('status')
                    error = TwitterUserTimelineError(job=job, user=tweep,
                                                     error=e)
                    error.save()
                    stop = True
                if stop:
                    break
