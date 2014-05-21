import getpass
import os
import stat
import datetime
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


def create_conf_file(twitterfilter_id):
    projectroot = settings.SFM_ROOT
    if hasattr(settings, 'SUPERVISOR_PROCESS_USER'):
        processowner = settings.SUPERVISOR_PROCESS_USER
    else:
        processowner = getpass.getuser()

    contents = "[program:twitterfilter-%s]" % twitterfilter_id + '\n' + \
               "command=%s/ENV/bin/python " % projectroot + \
               "%s/sfm/manage.py " % projectroot + \
               "filterstream %s --save" % twitterfilter_id + '\n' \
               "user=%s" % processowner + '\n' \
               "autostart=true" + '\n' \
               "autorestart=true" + '\n' \
               "stderr_logfile=/var/log/sfm/" \
               "twitterfilter-%s.err.log" % twitterfilter_id + '\n' \
               "stdout_logfile=/var/log/sfm/" \
               "twitterfilter-%s.out.log" % twitterfilter_id + '\n'
    filename = "twitterfilter-%s.conf" % twitterfilter_id
    file_path = "%s/sfm/sfm/supervisor.d/%s" % (projectroot, filename)
    # Remove any existing config file
    # we don't assume that the contents are up-to-date
    # (PATH settings may have changed, etc.)
    if os.path.exists(file_path):
        os.remove(file_path)
    # Write the file
    fp = open(file_path, "wb")
    fp.write(contents)
    filestatus = os.stat(file_path)
    # do a chmod +x
    os.chmod(file_path, filestatus.st_mode | stat.S_IXUSR |
             stat.S_IXGRP | stat.S_IXOTH)
    fp.close()


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
