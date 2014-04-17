from django.conf import settings
from django.core.management.base import BaseCommand

import os
import shutil
import time


class Command(BaseCommand):
    help = 'move data from the data_dir into date-structured dirs'

    def handle(self, *args, **options):
        # for every file in the data dir, eg:
        #   DATA/PREFIX-2012-04-22T17:33:44Z.xml.gz
        # if the modification time is greater than
        #   (2 * settings.SAVE_INTERVAL_SECONDS):
        # make sure there's a directory under DATA names PREFIX
        # make sure there's a DATA/PREFIX/2012/04/22
        # move it there, without changing its name
        data_files = os.listdir(settings.DATA_DIR)
        for fname in data_files:
            data_file = '%s/%s' % (settings.DATA_DIR, fname)
            stat = os.stat(data_file)
            threshhold_seconds = 2 * settings.SAVE_INTERVAL_SECONDS
            if time.time() - stat.st_mtime < threshhold_seconds:
                continue
            # pull out the prefix, year, month, day, and hour
            try:
                # patterns:
                #   twitterfilter-2-2014-04-11T04:34:28Z.gz
                #   sample-2014-04-11T04:34:28Z.gz
                prefixed_date, t, time_ext = fname.partition('T')
                # get process name by truncating last 11 chars: -YYYY-MM-DD
                processname = prefixed_date[:-11]
                # get date as the last 10 chars: YYYY-MM-DD
                the_date = prefixed_date[-10:]
                year, month, day = the_date.split('-')
                hour, minute, seconds_ext = time_ext.split(':')
            except:
                # probably a prefix/directory
                continue
            subdir = '%s/%s/%s/%s/%s/%s' % (settings.DATA_DIR, processname,
                                            year, month, day, hour)
            try:
                os.stat(subdir)
            except:
                os.makedirs(subdir)
            try:
                shutil.copy2(data_file, subdir)
                os.remove(data_file)
                print 'moved %s to %s' % (data_file, subdir)
            except Exception, e:
                print 'unable to move %s' % data_file
                print e
