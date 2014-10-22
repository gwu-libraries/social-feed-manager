from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
)

urlpatterns += patterns('ui.views',
    url(r'^$', 'home', name='home'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^django_no_superuser/$', TemplateView.as_view(template_name=
        'django_no_superuser.html'), name='django_no_superuser'),

    # twitter data patterns
    url(r'^search/$', 'search', name='search'),
    url(r'^tweets/$', 'tweets', name='tweets'),
    url(r'^users/alpha/$', 'users_alpha', name='users_alpha'),
    url(r'^twitter-user/(?P<name>[a-zA-Z0-9_]+)/$', 'twitter_user',
        name='twitter_user'),
    url(r'^twitter-user/(?P<name>[a-zA-Z0-9_]+).csv$', 'twitter_user_csv',
        name='twitter_user_csv'),
    url(r'^twitter-user/(?P<name>[a-zA-Z0-9_]+).xlsx', 'twitter_user_xls',
        name='twitter_user_xls'),
    url(r'^twitter-item/(?P<id>[0-9]+)/$', 'twitter_item',
        name='twitter_item'),
    url(r'^twitter-item/(?P<id>[0-9]+)/links/$', 'twitter_item_links',
        name='twitter_item_links'),
    url(r'^status/$', 'status', name='status'),

    url(r'', include('social_auth.urls')),
    )
