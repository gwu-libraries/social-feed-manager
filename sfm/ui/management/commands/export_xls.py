from optparse import make_option

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'export data for a twitteruser or setname in XLS format'

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
        make_option('--filename', action='store', default=None,
                    type='string', dest='filename',
                    help='filename to export'),
    )

    def handle(self, *args, **options):
        """Calls export_csv, passing all options plus --xls."""
        call_command('export_csv', start_date=options['start_date'],
                     end_date=options['end_date'],
                     twitter_user=options['twitter_user'],
                     set_name=options['set_name'],
                     filename=options['filename'],
                     xls=True)
