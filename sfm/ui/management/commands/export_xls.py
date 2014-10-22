import codecs
import sys
from optparse import make_option

from django.core.management import BaseCommand, call_command, CommandError


class Command(BaseCommand):
    help = 'export data for a twitteruser or setname in excel'

    option_list = BaseCommand.option_list + (
        make_option('--start-date', action='store', default=None,
                    type='string', dest='start_date',
                    help='earliest date (YYYY-MM-DD) for export'),
        make_option('--end-date', action='store', default=None,
                    type='string', dest='end_date',
                    help='latest date (YYYY-MM-DD) for export'),
        make_option('--twitter-user', action='store', default=None,
                    type='string', dest='twitter_user',
                    help='username to export'),
        make_option('--set-name', action='store', default=None,
                    type='string', dest='set_name',
                    help='set name to export'),
    )

    @classmethod
    def usage(self, *args):
        usage = 'Usage: ./manage.py export_xls [filename] ' + \
                '[options]' + '\n' + '\n' + self.help
        return usage

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("need a file name")
        extra_option = {}
        extra_option['xls'] = 'xls'
        extra_option['f_name'] = args[0] + '.xls'
        for opt in options:
            if options[opt] is not None:
                tuser = options['twitter_user']
                start_dt = options['start_date']
                end_dt = options['end_date']
                st_name = options['set_name']
                try:
                    call_command('export_csv', extra_option,
                                 twitter_user=tuser, start_date=start_dt,
                                 end_date=end_dt, set_name=st_name,)
                except Exception as e:
                    if sys.stderr:
                        print e
                    else:
                        try:
                            writer_class = codecs.getwriter('utf-8')
                            sys.stdout = writer_class(sys.stdout)
                        except Exception as e:
                            print e
            else:
                continue
