import os.path
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management import call_command

from ui.models import TwitterFilter


class Command(BaseCommand):
    help = "management command to save the process config files"
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
            contents = "[program:filterstream]" + '\n' + \
                       "command=<PATH TO YOUR SFM>/sfm/manage.py " \
                       "filtestream "  \
                       "--tfilterid=%s --save" % filterid.id + '\n' \
                       "environment=PATH=" \
                       "'<PATH TO YOUR SFM VIRTUALENV>/bin'" + '\n' \
                       "user=<YOUR PREFERRED SYSTEM USER>  " \
                       "(defaults to root otherwise)" + '\n' \
                       "autostart=true" + '\n' \
                       "autorestart=true" + '\n' \
                       "stderr_logfile=/var/log/filterstream.err.log" + '\n' \
                       "stdout_logfile=/var/log/filterstream.out.log"
        filename = "sfm-twitter-rule#%s-filter.conf" % filterid.id
        file_path = "<PATH TO SUPERVISOR CONF>/%s" % filename
        if os.path.exists(file_path):
            update_conf_file(file_path, filterid.id)
        else:
            fp = open(file_path, "wb")
            fp.write(contents)


def update_conf_file(file_path, filterid):
    os.remove(file_path)
    call_command('createconf', 'tfilterid=filterid')
