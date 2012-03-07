from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic import list_detail
from django.views.generic import TemplateView

from sfm.ui.models import Status

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
    url(r'^status/page/(?P<page>[0-9]+)/$', list_detail.object_list, 
        status_info, name='status_list'),
)
