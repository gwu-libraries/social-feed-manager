from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import list_detail
from django.views.generic import TemplateView

from ui.models import Status
from ui.views import StatusRuleListView

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

status_info = {
    'queryset': Status.objects.all(),
    'paginate_by': 50,
}

urlpatterns += patterns('ui.views',
    url(r'^$', 'home', name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^search/$', 'search', name='search'),
    url(r'^status/page/(?P<page>[0-9]+)/$', list_detail.object_list, 
        status_info, name='status_list'),
    url(r'^trends/weekly/$', 'trends_weekly', name='trends_weekly'),
    url(r'^trends/daily/$', 'trends_daily', name='trends_daily'),
)

urlpatterns += patterns('',
    url(r'^rule/(?P<rule>#?[a-zA-Z0-9_]+)/(?P<page>[0-9]+)/$', 
        StatusRuleListView.as_view(), name='rule'), 
)
