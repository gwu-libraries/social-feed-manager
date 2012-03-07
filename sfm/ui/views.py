from django.db.models import Count
from django.shortcuts import render

from ui.models import Status

def home(request):
    rules = Status.objects.values('rule_match').annotate(Count('rule_match')).order_by('-rule_match__count')
    tags = Status.objects.values('rule_tag').annotate(Count('rule_tag')).order_by('-rule_tag__count')
    return render(request, 'home.html', {
        'title': 'home',
        'rules': rules,
        'tags': tags,
        'statuses': Status.objects.all(),
        })
