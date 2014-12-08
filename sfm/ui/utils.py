import codecs
import cStringIO
import csv
import datetime
import getpass
import os
import stat
from supervisor import xmlrpc
import time
import traceback
import xmlrpclib
import xlwt
from xlwt import Workbook

from django.conf import settings
from django.utils import timezone

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
               "command=%s " % settings.PYTHON_EXECUTABLE + \
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
    # do a chmod +x, and add group write permissions
    os.chmod(file_path, filestatus.st_mode | stat.S_IXUSR |
             stat.S_IXGRP | stat.S_IXOTH | stat.S_IWGRP )
    fp.close()


def delete_conf_file(twitterfilter):
    filename = "twitterfilter-%s.conf" % twitterfilter
    file_path = "%s/sfm/sfm/supervisor.d/%s" % (settings.SFM_ROOT, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def get_supervisor_proxy():
    proxy = xmlrpclib.ServerProxy(
        'http://' + settings.INTERNAL_IPS[0],
        transport=xmlrpc.SupervisorTransport(
            None, None, 'unix://'+settings.SUPERVISOR_UNIX_SOCKET_FILE))
    return proxy


def add_process_group(filterid):
    proxy = get_supervisor_proxy()
    processname = "twitterfilter-%s" % filterid
    try:
        proxy.supervisor.addProcessGroup(processname)
    except xmlrpclib.Fault as e:
        if e.faultCode != xmlrpc.Faults.ALREADY_ADDED:
            raise
        # else ignore - it's already added
        # but everything else, we want to raise


def remove_process_group(filterid):
    proxy = get_supervisor_proxy()
    processname = "twitterfilter-%s" % filterid
    try:
        proxy.supervisor.stopProcess(processname, True)
    except xmlrpclib.Fault as e:
        if e.faultCode == xmlrpc.Faults.BAD_NAME:
            # process isn't known, so there's nothing to stop
            # or remove
            return
        elif e.faultCode != xmlrpc.Faults.NOT_RUNNING:
            raise
        # else ignore and proceed - it's already stopped
        # nothing to stop
    time.sleep(1)
    try:
        proxy.supervisor.removeProcessGroup(processname)
    except xmlrpclib.Fault as e:
        if e.faultCode != xmlrpc.Faults.BAD_NAME:
            raise
        # else do nothing - no such known process, so there's
        # nothing to remove


def reload_config():
    proxy = get_supervisor_proxy()
    proxy.supervisor.reloadConfig()


def process_info():
    proxy = get_supervisor_proxy()
    subprocess = proxy.supervisor.getAllProcessInfo()
    fail_process = ['FATAL', 'BACKOFF', 'STOPPED']
    process_detail = []
    for process_name in subprocess:
        info_detail = {}
        description = desc_days = desc_hour = desc_min = desc_sec = '0'
        stop_date = stop_time = start_date = start_time = 'NA'
        if 'twitterfilter' or 'streamsample' in process_name['name']:
            start_date = str(datetime.datetime.fromtimestamp(
                             process_name['start']).strftime('%m-%d-%Y'))
            start_time = str(datetime.datetime.fromtimestamp(
                             process_name['start']).strftime('%r'))
            status = process_name['statename']
            # description text for status running,
            if status == 'RUNNING':
                desc_time = process_name['description'].split(' ')
                desc_time_split = desc_time[-1]
                if len(desc_time_split) is 7:
                    desc_time_split = '0' + desc_time_split
                if len(desc_time) > 4:
                    desc_days = desc_time[-3]
                desc_hour = desc_time_split[0:2]
                desc_min = desc_time_split[3:5]
                desc_sec = desc_time_split[6:8]
        if status in fail_process:
            stop_date = str(datetime.datetime.fromtimestamp(
                            process_name['stop']).strftime('%m-%d-%Y'))
            stop_time = str(datetime.datetime.fromtimestamp(
                            process_name['stop']).strftime('%r'))
            #description text for failed status
            description = process_name['description']
            if status == 'STOPPED':
                description = '   '
            if status == 'BACKOFF':
                description = 'trying to start again'
        info_detail['name'] = process_name['name']
        info_detail['start_date'] = start_date
        info_detail['start_time'] = start_time
        info_detail['status'] = status
        info_detail['stop_date'] = stop_date
        info_detail['stop_time'] = stop_time
        info_detail['days'] = desc_days
        info_detail['hour'] = desc_hour
        info_detail['min'] = desc_min
        info_detail['sec'] = desc_sec
        info_detail['description'] = description
        process_detail.append(info_detail)
    return process_detail


def csv_tweets_writer(qs_tweets, fieldnames):
    """Returns a UnicodeCSVWriter object loaded with one row per tweet."""
    csvwriter = UnicodeCSVWriter()
    csvwriter.writerow(fieldnames)
    for t in qs_tweets:
        csvwriter.writerow(t.csv)
    return csvwriter


def xls_tweets_workbook(qs_tweets, fieldnames):
    """Returns an XLS Workbook object with one row per tweet."""
    new_workbook = Workbook(encoding="UTF-8")
    new_sheet = new_workbook.add_sheet('sheet1')
    font = xlwt.Font()
    font.name = 'Arial Unicode MS'
    style = xlwt.XFStyle()
    style.font = font
    for i in range(0, len(fieldnames)):
        new_sheet.write(0, i, fieldnames[i], style=style)
        row = 0
    for t in qs_tweets:
        row = row+1
        col = 0
        for r in range(0, len(t.csv)):
            new_sheet.write(row, col, t.csv[r], style=style)
            col = col+1
    return new_workbook


class UnicodeCSVWriter:

    def __init__(self, dialect=csv.excel, encoding='utf-8', **params):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **params)
        self.encoding = encoding
        self.encoder = codecs.getincrementalencoder(self.encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def out(self):
        return cStringIO.StringIO(self.queue.getvalue())
