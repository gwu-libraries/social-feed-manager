from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import render, redirect

from ui.models import TwitterUserItem, TrendWeekly, TrendDaily

def home(request):
    user_item_counts = TwitterUserItem.objects.values('twitter_user', 'twitter_user__name').annotate(Count('twitter_user')).order_by('-twitter_user__count')
    return render(request, 'home.html', {
        'title': 'home',
        'user_item_counts': user_item_counts,
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
