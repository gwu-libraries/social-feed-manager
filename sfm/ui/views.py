from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import render, redirect
from django.views.generic import ListView

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
        
class StatusRuleListView(ListView):

    template_name = 'ui/status_by_rule_list.html'

    def get_queryset(self):
        return Status.objects.filter(rule_match__iexact=self.kwargs['rule'])

    def get_context_data(self, **kwargs):
        context = super(StatusRuleListView, self).get_context_data(**kwargs)
        qs = self.get_queryset()
        paginator = Paginator(qs, 50)
        try: 
            page = int(self.kwargs.get('page', 1))
        except ValueError:
            page = 1
        try:
            results = paginator.page(page)
        except (EmptyPage, InvalidPage):
            results = paginator.page(paginator.num_pages)
        context['rule'] = self.kwargs['rule']
        context['paginator'] = paginator
        context['page_obj'] = results
        context['object_list'] = results.object_list
        return context

