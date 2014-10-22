import codecs
import cStringIO
import csv
import os
import xlwt
from xlwt import Workbook

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import TwitterUser, TwitterUserItem
from .utils import process_info, write_xls


def _paginate(request, paginator):
    page = request.GET.get('page', 1)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return page, items


@login_required
def home(request):
    qs_users = TwitterUser.objects.all()
    qs_users_alpha = qs_users.order_by('?')
    qs_items = TwitterUserItem.objects.order_by('-date_published')
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DATE_TRUNC('day', date_published) AS day,
                   COUNT(*) AS item_count
            FROM ui_twitteruseritem
            WHERE date_published > NOW() - INTERVAL '1 month'
            GROUP BY 1
            ORDER BY day
            LIMIT 31 OFFSET 1;
            """)
        daily_counts = [[row[0].strftime('%Y-%m-%d'), int(row[1])]
                        for row in cursor.fetchall()]
        # Workaround for known "slow count(*)" issue
        cursor.execute("""
            SELECT reltuples FROM pg_class WHERE relname='ui_twitteruseritem'
            """)
        item_count = int(cursor.fetchone()[0])
    except:
        daily_counts = []
        item_count = 0
    return render(request, 'home.html', {
        'title': 'home',
        'users': qs_users,
        'users_alpha': qs_users_alpha[:25],
        'items': qs_items[:10],
        'item_count': item_count,
        'daily_counts': daily_counts,
    })


@login_required
def search(request):
    q = request.GET.get('q', '')
    title = ''
    if q:
        qs_users = TwitterUser.objects.filter(name__icontains=q)
        qs_users = qs_users.extra(select={'lower_name': 'lower(name)'})
        qs_users = qs_users.order_by('lower_name')
        title = 'search: "%s"' % q
    return render(request, 'search.html', {
        'title': title,
        'users': qs_users,
        'q': q,
    })


@login_required
def tweets(request):
    qs_tweets = TwitterUserItem.objects.order_by('-date_published')
    paginator = Paginator(qs_tweets, 50)
    page, tweets = _paginate(request, paginator)
    return render(request, 'tweets.html', {
        'title': 'all tweets, chronologically',
        'tweets': tweets,
        'paginator': paginator,
        'page': page,
    })


@login_required
def users_alpha(request):
    qs_users = TwitterUser.objects.all()
    qs_users = qs_users.extra(select={'lower_name': 'lower(name)'})
    qs_users = qs_users.order_by('lower_name')
    paginator = Paginator(qs_users, 25)
    page, users = _paginate(request, paginator)
    return render(request, 'users_alpha.html', {
        'title': 'all users, alphabetically',
        'users': users,
        'paginator': paginator,
        'page': page,
    })


@login_required
def twitter_user(request, name=''):
    user = get_object_or_404(TwitterUser, name=name)
    qs_tweets = user.items.order_by('-date_published')
    # grab a slightly older tweet to use for bio info
    if qs_tweets.count() > 20:
        recent_tweet = qs_tweets[20]
    elif qs_tweets.count() > 0:
        recent_tweet = qs_tweets[0]
    else:
        recent_tweet = None
    paginator = Paginator(qs_tweets, 50)
    page, tweets = _paginate(request, paginator)
    # fetch 90 days' worth of counts
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DATE_TRUNC('day', date_published) AS day,
                   COUNT(*) AS item_count
                   FROM ui_twitteruseritem
            WHERE twitter_user_id = %s
                AND date_published > NOW() - INTERVAL '3 months'
            GROUP BY 1
            ORDER BY day
            LIMIT 91 OFFSET 1;
        """ % (user.id))
        daily_counts = [[row[0].strftime('%Y-%m-%d'), int(row[1])]
                        for row in cursor.fetchall()]
    except:
        daily_counts = []
    return render(request, 'twitter_user.html', {
        'title': 'twitter user: %s' % name,
        'twitter_user': user,
        'qs_tweets': qs_tweets,
        'tweets': tweets,
        'recent_tweet': recent_tweet,
        'daily_counts': daily_counts,
        'paginator': paginator,
        'page': page,
    })


@login_required
def twitter_user_csv(request, name=''):
    fieldnames = ['sfm_id', 'created_at', 'created_at_date', 'twitter_id',
                  'screen_name', 'followers_count', 'friends_count',
                  'retweet_count', 'hashtags', 'in_reply_to_screen_name',
                  'mentions', 'twitter_url', 'is_retweet_strict', 'is_retweet',
                  'text', 'url1', 'url1_expanded', 'url2', 'url2_expanded']
    user = get_object_or_404(TwitterUser, name=name)
    qs_tweets = user.items.order_by('-date_published')
    csvwriter = UnicodeCSVWriter()
    csvwriter.writerow(fieldnames)
    for t in qs_tweets:
        csvwriter.writerow(t.csv)
    response = StreamingHttpResponse(csvwriter.out(), content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="%s.csv"' % name
    return response


@login_required
def twitter_user_xls(request, name=''):
    user = get_object_or_404(TwitterUser, name=name)
    qs_tweets = user.items.order_by('-date_published')
    new_workbook = write_xls(qs_tweets)
    response = HttpResponse(content_type='text/ms-excel')
    response['Content-Disposition'] = \
        'attachment; filename="%s.xls"' % name
    new_workbook.save(response)
    return response


@login_required
def twitter_item(request, id=0):
    item = get_object_or_404(TwitterUserItem, id=int(id))
    return HttpResponse(item.item_json, content_type='application/json')


@login_required
def twitter_item_links(request, id=0):
    item = get_object_or_404(TwitterUserItem, id=int(id))
    unshortened = [item.unshorten(l) for l in item.links]
    return render(request, 'twitter_item_links.html', {
        'item': item,
        'unshortened': unshortened,
    })


def logout(request):
    auth.logout(request)
    return redirect(reverse('home'))


#redirect to new page in case not superuser
@user_passes_test(lambda u: u.is_superuser, login_url='django_no_superuser')
def status(request):
    if os.path.exists(settings.SUPERVISOR_UNIX_SOCKET_FILE):
        proc_status = process_info()
        return render(request, 'status.html', {
            'list': proc_status,
            })
    else:
        return render(request, 'status_not_found.html')


class UnicodeCSVWriter:

    def __init__(self, dialect=csv.excel, encoding='utf-8', **params):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **params)
        self.encoding = encoding
        self.encoder = codecs.getincrementalencoder(self.encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def out(self):
        return cStringIO.StringIO(self.queue.getvalue())


