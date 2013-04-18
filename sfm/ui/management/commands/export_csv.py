import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ui.models import TwitterUser, TwitterUserSet, TwitterUserItem

def make_date_aware(date_str):
    """take a date in the format YYYY-MM-DD and return an aware date"""
    try:
        year, month, day = [int(x) for x in date_str.split('-')]
        dt = datetime.datetime(year, month, day)
        dt_aware = timezone.make_aware(dt, 
                timezone.get_current_timezone())
        return dt_aware
    except:
        import traceback
        print traceback.print_exc()
        return None


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
        # FIXME: why use options.get again and again? 
        twitter_user = None
        user_set = None
        start_dt = None
        end_dt = None
        if options.get('twitter_user', False):
            try:
                twitter_user = TwitterUser.objects.get(
                        name=options.get('twitter_user'))
            except TwitterUser.DoesNotExist:
                raise CommandError('TwitterUser %s does not exist' % \
                        options.get('twitter_user'))
        elif options.get('set_name', False):
            user_set = None
            try:
                user_set = TwitterUserSet.objects.get(
                        name=options.get('set_name'))
            except TwitterUserSet.DoesNotExist:
                raise CommandError('TwitterUserSet %s does not exist' % \
                        options.get('set_name'))
        else:
            raise CommandError('please specify a twitter user or set name')

        if options.get('start_date', False):
            start_dt = make_date_aware(options.get('start_date'))
            if not start_dt:
                raise CommandError('dates must be in the format YYYY-MM-DD')
        else:
            start_dt = None
        if options.get('end_date', False):
            end_dt = make_date_aware(options.get('end_date'))
            if not end_dt:
                raise CommandError('dates must be in the format YYYY-MM-DD')
        else:
            end_dt = None
        if start_dt and end_dt:
            if end_dt < start_dt:
                raise CommandError('start date must be earlier than end date')

        if twitter_user:
            qs = twitter_user.items.all()
        elif user_set:
            qs = TwitterUserItem.objects.filter(
                    twitter_user__sets__in=[user_set])

        if start_dt:
            qs = qs.filter(date_published__gte=start_dt)
        if end_dt:
            qs = qs.filter(date_published__lte=end_dt)

        for tui in qs:
            print '\t'.join(tui.csv)
