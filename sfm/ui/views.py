from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import TrendWeekly, TrendDaily
from .models import TwitterUser, TwitterUserItem

def home(request):
    user_item_counts = TwitterUserItem.objects.values('twitter_user', 'twitter_user__name').annotate(Count('twitter_user')).order_by('-twitter_user__count')
    return render(request, 'home.html', {
        'title': 'home',
        'user_item_counts': user_item_counts,
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

def twitter_item(request, id=0):
    item = get_object_or_404(TwitterUserItem, id=int(id))
    return HttpResponse(item.item_json, content_type="application/json")

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
