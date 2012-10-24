import codecs
import cStringIO
import csv

from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import TrendWeekly, TrendDaily
from .models import TwitterUser, TwitterUserItem, DATES

def home(request):
    user_item_counts = TwitterUserItem.objects.values('twitter_user', 'twitter_user__name').annotate(Count('twitter_user')).order_by('-twitter_user__count')
    users = {}
    for uic in user_item_counts:
        users[uic['twitter_user__name']] = TwitterUser.objects.get(id=uic['twitter_user'])
    return render(request, 'home.html', {
        'title': 'home',
        'user_item_counts': user_item_counts,
        'users': users,
        'dates': DATES,
        })

def twitter_user(request, name='', page=0):
    user = get_object_or_404(TwitterUser, name=name)
    if page < 1:
        page = 1
    qs_tweets = user.items.order_by('-date_published')
    # grab a slightly older tweet to use for bio info
    if qs_tweets.count() > 20:
        recent_tweet = qs_tweets[25]
    elif qs_tweets.count() > 0:
        recent_tweet = qs_tweets[0]
    else:
        recent_tweet = None
    paginator = Paginator(qs_tweets, 50)
    try:
        tweets = paginator.page(page)
    except PageNotAnInteger:
        tweets = paginator.page(0)
    except EmptyPage:
        tweets = paginator.page(paginator.num_pages)
    return render(request, 'twitter_user.html', {
        'title': 'twitter user: %s' % name,
        'user': user,
        'qs_tweets': qs_tweets,
        'tweets': tweets,
        'recent_tweet': recent_tweet,
        })

def twitter_user_csv(request, name=''):
    fieldnames = ['sfm_id', 'created_at', 'twitter_id', 'screen_name', 
            'followers_count', 'friends_count', 'retweet_count', 
            'hashtags', 'twitter_url', 'text']
    user = get_object_or_404(TwitterUser, name=name)
    qs_tweets = user.items.order_by('-date_published')
    #out = ['\t'.join(t.csv) for t in qs_tweets]
    csvwriter = UnicodeCSVWriter()
    csvwriter.writerow(fieldnames)
    for t in qs_tweets:
        csvwriter.writerow(t.csv)
    response = HttpResponse(csvwriter.out(), content_type='text/csv')
    response['Content-Disposition'] = \
            'attachment; filename="%s.csv"' % name
    return response

def twitter_item(request, id=0):
    item = get_object_or_404(TwitterUserItem, id=int(id))
    return HttpResponse(item.item_json, content_type='application/json')

def twitter_item_links(request, id=0):
    item = get_object_or_404(TwitterUserItem, id=int(id))
    unshortened = [item.unshorten(l) for l in item.links]
    return render(request, 'twitter_item_links.html', {
        'item': item,
        'unshortened': unshortened,
        })

def trends_weekly(request):
    trends = TrendWeekly.objects.all()  
    return render(request, 'trends_weekly.html', {
        'trends': trends,
        })

def trends_daily(request):
    trends = TrendDaily.objects.all()  
    return render(request, 'trends_daily.html', {
        'trends': trends,
        })

def logout(request):
    auth.logout(request)
    return redirect(reverse('home'))

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
        return self.queue.getvalue()
