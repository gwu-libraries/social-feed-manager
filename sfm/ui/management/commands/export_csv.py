import codecs
from optparse import make_option
import sys
from django.core.management.base import BaseCommand, CommandError

from ui.models import TwitterUser, TwitterUserSet, TwitterUserItem
from ui.utils import make_date_aware, xls_tweets_workbook


class Command(BaseCommand):
    help = 'export data for a user or a set in csv or xls'

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
        make_option('--xls', action='store_true', default=False,
                    dest='xls', help='export in .xls format'),
        make_option('--filename', action='store', default=None,
                    type='string', dest='filename',
                    help='filename to export (required with --xls)'),
    )

    def handle(self, *args, **options):
        twitter_user = user_set = start_dt = end_dt = xls = filename = None
        if options['filename']:
            filename = options.get('filename')
        xls = options['xls']
        if xls and filename is None:
            raise CommandError("When --xls is specified, \
--filename=FILENAME is required")
        if not xls and filename is not None:
            raise CommandError("Writing CSV files currently not yet \
supported; recommend piping output to a file")
        if options['twitter_user']:
            try:
                twitter_user = TwitterUser.objects.get(
                    name=options.get('twitter_user'))
                qs = twitter_user.items.all()
            except TwitterUser.DoesNotExist:
                raise CommandError('TwitterUser %s does not exist' %
                                   options.get('twitter_user'))
        elif options['set_name']:
            try:
                user_set = TwitterUserSet.objects.get(
                    name=options.get('set_name'))
                qs = TwitterUserItem.objects.filter(
                    twitter_user__sets__in=[user_set])
            except TwitterUserSet.DoesNotExist:
                raise CommandError('TwitterUserSet %s does not exist' %
                                   options['set_name'])
        else:
            raise CommandError('please provide either twitteruser or setname')
        if options['start_date']:
            start_dt = make_date_aware(options.get('start_date'))
            if not start_dt:
                raise CommandError('dates must be in the format YYYY-MM-DD')
            qs = qs.filter(date_published__gte=start_dt)
        if options['end_date']:
            end_dt = make_date_aware(options.get('end_date'))
            if not end_dt:
                raise CommandError('dates must be in the format YYYY-MM-DD')
            qs = qs.filter(date_published__lte=end_dt)
        if start_dt and end_dt:
            if end_dt < start_dt:
                raise CommandError('start date must be earlier than end date')
        # tweak for python 2.7 to avoid having to set PYTHONIOENCODING=utf8
        # in environment, see Graham Fawcett's comment/suggestion at:
        #   nedbatchelder.com/blog/200401/printing_unicode_from_python.html
        writer_class = codecs.getwriter('utf-8')
        sys.stdout = writer_class(sys.stdout, 'replace')
        if xls:
            tworkbook = xls_tweets_workbook(qs, TwitterUserItem.csv_headers)
            tworkbook.save(filename)
        else:
            for tui in qs:
                print '\t'.join(tui.csv)
