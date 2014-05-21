import datetime
import os
from supervisor.xmlrpc import SupervisorTransport
import time
import traceback
import xmlrpclib

from django.utils import timezone

from django.conf import settings


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


def make_date_aware(date_str):
    """take a date in the format YYYY-MM-DD and return an aware date"""
    try:
        year, month, day = [int(x) for x in date_str.split('-')]
        dt = datetime.datetime(year, month, day)
        dt_aware = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt_aware
    except:
        print traceback.print_exc()
        return None


def delete_conf_file(twitterfilter):
    filename = "twitterfilter-%s.conf" % twitterfilter
    file_path = "%s/sfm/sfm/supervisor.d/%s" % (settings.SFM_ROOT, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def get_supervisor_proxy():
    proxy = xmlrpclib.ServerProxy(
        'http://127.0.0.1', transport=SupervisorTransport(
            None, None, 'unix://'+settings.SUPERVISOR_UNIX_SOCKET_FILE))
    return proxy


def add_process_group(filterid):
    proxy = get_supervisor_proxy()
    filename = "twitterfilter-%s" % filterid
    proxy.supervisor.addProcessGroup(filename)


def remove_process_group(filterid):
    proxy = get_supervisor_proxy()
    filename = "twitterfilter-%s" % filterid
    proxy.supervisor.stopProcess(filename, True)
    proxy.supervisor.removeProcessGroup(filename)
