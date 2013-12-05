from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from ui.models import authenticated_api
from ui.models import TwitterUser
from ui.utils import populate_uid


class Command(BaseCommand):
    """
    Cycle through all the TwitterUsers we're tracking.  For each TwitterUser,
    if the uid==0 (default value, i.e. it hasn't been set yet), look the
    user up by name and populate the uid.
    """

    help = 'Fetch uids for twitter users by name, where uids ' \
           + 'are not populated.  Intended for migrating old ' \
           + 'databases prior to m2_001.'

    option_list = BaseCommand.option_list + (
        make_option('--user', dest='user',
                    default=None, help='Specific user to update'),
    )

    def handle(self, *args, **options):
        api = authenticated_api(username=settings.TWITTER_DEFAULT_USERNAME)
        qs_tweeps = TwitterUser.objects.filter(is_active=True)
        # if a username has been specified, limit to only that user
        if options.get('user', None):
            qs_tweeps = qs_tweeps.filter(name=options.get('user'))
        for tweep in qs_tweeps:
            print 'user: %s' % tweep.name
            # check user status, update twitter user name if it has changed
            populate_uid(tweep.name, api)
