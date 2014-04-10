import getpass
import os
import stat
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from ui.models import TwitterFilter


class Command(BaseCommand):
    help = "create/update filterstream process config files for supervisord"
    option_list = BaseCommand.option_list + (
        make_option('--twitterfilter', action='store', default=None,
                    dest='twitterfilter', help='specify the filter rule id'),
        )

    def handle(self, *args, **options):
        twitter_filters = TwitterFilter.objects.filter(is_active=True)
        if options.get('twitterfilter', None):
            twitter_filters = twitter_filters.filter(
                id=options.get('twitterfilter'))
        projectroot = settings.SFM_ROOT
        if settings.SUPERVISOR_PROCESS_USER:
            processowner = settings.SUPERVISOR_PROCESS_USER
        else:
            processowner = getpass.getuser()
        for tf in twitter_filters:
            contents = "[program:filterstream-%s]" % tf.id + '\n' + \
                       "command=%s/ENV/bin/python " % projectroot + \
                       "%s/sfm/manage.py " % projectroot + \
                       "filterstream %s --save" % tf.id + '\n' \
                       "user=%s" % processowner + '\n' \
                       "autostart=true" + '\n' \
                       "autorestart=true" + '\n' \
                       "stderr_logfile=/var/log/" \
                       "sfm-filterstream-%s.err.log" % tf.id + '\n' \
                       "stdout_logfile=/var/log/" \
                       "sfm-filterstream-%s.out.log" % tf.id + '\n'
            filename = "sfm-twitter-filter-%s.conf" % tf.id
            file_path = "%s/sfm/sfm/supervisor.d/%s" % (projectroot, filename)
            # Remove any existing config file
            # we don't assume that the contents are up-to-date
            # (PATH settings may have changed, etc.)
            if os.path.exists(file_path):
                os.remove(file_path)
                print "Removed old configuration file for TwitterFilter %d" % \
                    tf.id

            fp = open(file_path, "wb")
            fp.write(contents)
            filestatus = os.stat(file_path)
            # do a chmod +x
            os.chmod(file_path, filestatus.st_mode | stat.S_IXUSR |
                     stat.S_IXGRP | stat.S_IXOTH)
            fp.close()
            print "Created configuration file for TwitterFilter %d" % \
                  tf.id
