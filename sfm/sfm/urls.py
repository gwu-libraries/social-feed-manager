from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login',
        kwargs={'extra_context': {'branding': settings.BRANDING}}),
)

urlpatterns += patterns('ui.views',
    url(r'^$', 'home', name='home'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about', kwargs={'branding': settings.BRANDING}),

    # twitter data patterns
    url(r'^search/$', 'search', name='search'),
    url(r'^tweets/$', 'tweets', name='tweets'),
    url(r'^users/alpha/$', 'users_alpha', name='users_alpha'),
    url(r'^twitter-user/(?P<name>[a-zA-Z0-9_]+)/$', 'twitter_user', 
        name='twitter_user'),
    url(r'^twitter-user/(?P<name>[a-zA-Z0-9_]+).csv$', 'twitter_user_csv',
        name='twitter_user_csv'),
    url(r'^twitter-item/(?P<id>[0-9]+)/$', 'twitter_item',
        name='twitter_item'),
    url(r'^twitter-item/(?P<id>[0-9]+)/links/$', 'twitter_item_links',
        name='twitter_item_links'),

    url(r'', include('social_auth.urls')),
)

