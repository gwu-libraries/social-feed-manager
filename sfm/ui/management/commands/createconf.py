from optparse import make_option

from django.core.management.base import BaseCommand

from ui.models import TwitterFilter
from ui.utils import create_conf_file


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
        for tf in twitter_filters:
            create_conf_file(tf.id)
