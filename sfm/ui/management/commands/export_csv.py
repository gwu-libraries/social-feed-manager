import codecs
from optparse import make_option
import sys
from django.core.management.base import BaseCommand, CommandError

from ui.models import TwitterUser, TwitterUserSet, TwitterUserItem
from ui.utils import make_date_aware, write_xls


class Command(BaseCommand):
    help = 'export data for a user or a set in csv'

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

    def handle(self, *args, **options):
        twitter_user = user_set = start_dt = end_dt = if_xls = f_name = None
        for idx in args:
            if len(args) == 0:
                continue
            elif len(args) == 1:
                try:
                    idx['xls'] = 'xls'
                    if_xls = 'Y'
                    f_name = idx['f_name']
                except Exception:
                    raise CommandError("please user --help to check usage")
            else:
                raise CommandError("please use --help to check usage")
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
        if if_xls is 'Y':
            new_workbook = write_xls(qs)
            new_workbook.save(f_name)
            print "File created"
        else:
            for tui in qs:
                print '\t'.join(tui.csv)
