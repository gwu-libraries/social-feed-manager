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

import time
import tweepy
from django.conf import settings
from ui.models import authenticated_api
from ui.models import TwitterUser

# A little added cushion
WAIT_BUFFER_SECONDS = 2


def set_wait_time(last_response):
    """based on last tweepy api response, calculate a time buffer in
    seconds to wait before issuing next api call."""
    wait_time = 0
    try:
        remaining = int(last_response.getheader('x-rate-limit-remaining'))
        reset = int(last_response.getheader('x-rate-limit-reset'))
        reset_seconds = reset - int(time.time())
    except:
        remaining = reset_seconds = 1
    # the out-of-calls-for-this-window case
    if remaining == 0:
        return reset_seconds + WAIT_BUFFER_SECONDS
    else:
        wait_time = (reset_seconds / remaining) + WAIT_BUFFER_SECONDS
    # #22: saw some negative ratelimit-reset/wait_times
    # so cushion around that too
    while wait_time < WAIT_BUFFER_SECONDS:
        wait_time += WAIT_BUFFER_SECONDS
    return wait_time


# For a TwitterUser, populate its uid based on its stored screen name,
# if uid==0 (default value, indicating it hasn't been set yet).
# if force==True, do it even if uid isn't 0
# Only do this for active users.
#
# see https://dev.twitter.com/docs/api/1.1/get/users/lookup
#   for explanation of get_user call
# see https://dev.twitter.com/docs/working-with-timelines
#   for explanation of max_id, since_id usage
# see also:
#   https://dev.twitter.com/docs/error-codes-responses
#   https://dev.twitter.com/docs/rate-limiting


def populate_uid(name, force=False):
    #TODO: if user is None:

    api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
    qs_tweeps = TwitterUser.objects.filter(is_active=True, name=name)
    #TODO: What if we didn't find someone with that name?
    for tweep in qs_tweeps:
        if tweep.uid == 0 or force is True:
            try:
                #TODO: better way to catch when user isn't found
                user_status = api.get_user(screen_name=name)
                tweep.uid = user_status['id']
                tweep.save()
                print 'updated user \'%s\' uid to %d' % (name, tweep.uid)
            except tweepy.error.TweepError as e:
                print 'Failed to find user \'%s\'. Error: %s' % (name, e)
            finally:
                time.sleep(set_wait_time(api.last_response))
