import os
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
            contents = "[program:filterstream]" + '\n' + \
                       "command=%s/manage.py " % settings.SFMPATH + \
                       "filterstream "  \
                       "--tfilterid=%s --save" % filterid.id + '\n' \
                       "environment=PATH=" \
                       "'%s/bin'" % settings.SFMENV + '\n' \
                       "user=%s (defaults to root otherwise)" \
                       % settings.USER + '\n' \
                       "autostart=true" + '\n' \
                       "autorestart=true" + '\n' \
                       "stderr_logfile=/var/log/filterstream.err.log" + '\n' \
                       "stdout_logfile=/var/log/filterstream.out.log"
        filename = "sfm-twitter-filter-%s.conf" % filterid.id
        file_path = "%s/%s" % (settings.FILEPATH, filename)
        if os.path.exists(file_path):
            update_conf_file(file_path, filterid.id)
        else:
            fp = open(file_path, "wb")
            fp.write(contents)


def update_conf_file(file_path, filterid):
    if os.path.exists(file_path):
        os.remove(file_path)
    call_command('createconf', 'tfilterid=filterid')
