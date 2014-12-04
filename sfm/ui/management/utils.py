import datetime
from django.core.management.base import CommandError
from ui.models import TwitterFilter
from datetime import datetime


def parse_date(date_str):
    """
    Parses a YYYY-MM-DD into a Date.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str is not None else None
    except:
        raise CommandError("%s is not YYYY-MM-DD" % date_str)


def get_stream_basename(name):
    """
    Get the basename used to name stream directories and files.
    """
    if name:
        #Lookup filter id from name.
        try:
            twitter_filter = TwitterFilter.objects.get(
                name__iexact=name)
        except TwitterFilter.DoesNotExist:
            raise CommandError('Filter %s does not exists' % name)
        return "twitterfilter-%s" % twitter_filter.id
    else:
        return "streamsample"


def include_dir(include_dir, base_dir, start_date, end_date):
    """
    Filters a tweet file data directory based on date.
    """
    rel_dir = include_dir[len(base_dir)+1:]
    #Must have 10 characters to have a complete date
    if len(rel_dir) >= 10:
        dir_date = datetime.strptime(rel_dir[0:10], "%Y/%m/%d").date()
        if (start_date is None or dir_date >= start_date) and (end_date is None or dir_date <= end_date):
            return True
        else:
            return False
    else:
        #Less than 10 characters
        return True
