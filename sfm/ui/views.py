from django.contrib import auth
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import render, redirect

from ui.models import Status, TrendWeekly, TrendDaily

def home(request):
    rules = Status.objects.values('rule_match').annotate(Count('rule_match')).order_by('-rule_match__count')
    tags = Status.objects.values('rule_tag').annotate(Count('rule_tag')).order_by('-rule_tag__count')
    return render(request, 'home.html', {
        'title': 'home',
        'rules': rules,
        'tags': tags,
        'statuses': Status.objects.all(),
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
