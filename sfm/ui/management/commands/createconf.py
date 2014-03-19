import os
import stat
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from ui.models import TwitterFilter


class Command(BaseCommand):
    help = "command to save the process config files for supervisord"
    option_list = BaseCommand.option_list + (
        make_option('--tfilterid', action='store', default=None,
                    dest='tfilterid', help='specify the filter rule id'),
        )

    def handle(self, *args, **options):
        twitter_filters = TwitterFilter.objects.filter(is_active=True)
        if options.get('tfilterid', None):
            twitter_filters = twitter_filters.filter(
                id=options.get('tfilterid'))
        for filterid in twitter_filters:
            contents = "[program:filterstream-%s]" % filterid.id + '\n' + \
                       "command=%s/manage.py " % settings.SFM_LOCATION + \
                       "filterstream "  \
                       "--tfilterid=%s --save" % filterid.id + '\n' \
                       "environment=PATH=" \
                       "'%s/bin'" % settings.SFM_ENV_PATH + '\n' \
                       "user=%s" % settings.SUPERVISOR_PROCESS_USER + '\n' \
                       "autostart=true" + '\n' \
                       "autorestart=true" + '\n' \
                       "stderr_logfile=/var/log/filterstream/" \
                       "filterstream-%s.err.log" % filterid.id + '\n' \
                       "stdout_logfile=/var/log/filterstream/" \
                       "filterstream.out.log"
            filename = "sfm-twitter-filter-%s.conf" % filterid.id
            file_path = "%s/%s" % (settings.FILEPATH, filename)
            if os.path.exists(file_path):
                update_conf_file(file_path, filterid.id)
            else:
                fp = open(file_path, "wb")
                fp.write(contents)
                filestatus = os.stat(file_path)
                # do a chmod +w
                os.chmod(file_path, filestatus.st_mode | stat.S_IXUSR |
                         stat.S_IXGRP | stat.S_IXOTH)
                fp.close()


def update_conf_file(file_path, filterid):
    os.remove(file_path)
    call_command('createconf', tfilterid=filterid)
