from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import render, redirect

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

def search(request):
    q = request.GET.get('q', '')
    if q:
        qs_results = Status.objects.filter(summary__icontains=q)
        paginator = Paginator(qs_results, 50)
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1
        try:
            results = paginator.page(page)
        except (EmptyPage, InvalidPage):
            results = paginator.page(paginator.num_pages)
        return render(request, 'search.html', {
            'title': 'search "%s"' % q,
            'q': q,
            'paginator': paginator,
            'page_obj': results,
            'object_list': results.object_list,
            })
    return redirect(reverse('home'))
        
