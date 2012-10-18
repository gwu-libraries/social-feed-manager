from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

import datetime

from ui.models import DATES, DailyTwitterUserItemCount
from ui.models import TwitterUser, TwitterUserItem


class Command(BaseCommand):
    help = 'generate daily counts for each user, tweets per day'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('DELETE FROM ui_dailytwitteruseritemcount')
        transaction.commit_unless_managed()
        qs_twitter_users = TwitterUser.objects.all()
        for twitter_user in qs_twitter_users:
            print 'user:', twitter_user
            for dt in DATES:
                dt_aware = timezone.make_aware(dt, timezone.utc)
                count = TwitterUserItem.objects.filter(
                    date_published__year=dt_aware.year, 
                    date_published__month=dt_aware.month, 
                    date_published__day=dt_aware.day, 
                    twitter_user=twitter_user).count() 
                dtuic = DailyTwitterUserItemCount(twitter_user=twitter_user,
                    date=dt_aware, num_tweets=count)
                dtuic.save()
                print 'user %s, date %s, count %s' % (twitter_user, 
                    dt_aware, count)
