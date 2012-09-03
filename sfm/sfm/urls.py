from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

from ui.views import StatusRuleListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
)

urlpatterns += patterns('ui.views',
    url(r'^$', 'home', name='home'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^trends/weekly/$', 'trends_weekly', name='trends_weekly'),
    url(r'^trends/daily/$', 'trends_daily', name='trends_daily'),
)

urlpatterns += patterns('',
    url(r'^rule/(?P<rule>#?[a-zA-Z0-9_]+)/(?P<page>[0-9]+)/$', 
        StatusRuleListView.as_view(), name='rule'), 
)
