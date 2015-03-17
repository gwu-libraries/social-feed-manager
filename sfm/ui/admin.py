from django.contrib import admin
from django.contrib import messages

import tweepy
from ui import models as m
from django.conf import settings


class TwitterFilterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'is_active', 'words', 'people',
                    'locations']
    list_filter = ['is_active']
    search_fields = ['name', 'words', 'people', 'locations']
    fields = ('name', 'user', 'is_active', 'words', 'people', 'locations')

    def save_model(self, request, obj, form, change):
        ppl = []
        uids = []
        ppl_fetched = set()
        if 'people' in form.changed_data:
            for person in obj.people.split(','):
                ppl.append(person.lstrip().rstrip())
            try:
                if obj.people != '':
                    api = m.authenticated_api(username=
                                              settings.TWITTER_DEFAULT_USERNAME
                                              )
                    people_uids = api.lookup_users(screen_names=ppl)
                    for person in range(0, len(people_uids)):
                        uids.append(people_uids[person]['id'])
                        ppl_fetched.add(str(people_uids[person]
                                            ['screen_name']).lower())
                    obj.uids = ', '.join(map(str, uids))
                    ppl_form = set(n.lower() for n in ppl)
                    if ppl_form - ppl_fetched != set():
                        diff = ppl_form - ppl_fetched
                        messages.add_message(request, messages.WARNING,
                                             'TwitterFilter %s was saved '
                                             'with the following invalid '
                                             'accounts: %s' %
                                             (obj, ', '.join(map(str, diff))))
                else:
                    obj.uids = ''
            except Exception as e:
                if tweepy.error.TweepError:
                    e = e[0][0]['message']
                messages.add_message(request, messages.WARNING,
                                     'TwitterFilter %s was saved with the '
                                     'an exception: %s' % (obj, e))
        super(TwitterFilterAdmin, self).save_model(request, obj, form, change)


admin.site.register(m.TwitterFilter, TwitterFilterAdmin)


class TwitterUserAdmin(admin.ModelAdmin):
    fields = ('name', 'is_active', 'uid', 'former_names', 'sets',
              'date_last_checked')
    list_display = ['id', 'is_active', 'uid', 'name', 'former_names',
                    'date_last_checked']
    list_filter = ['is_active']
    search_fields = ['name', 'former_names', 'uid']
    filter_horizontal = ['sets']

    def get_readonly_fields(self, request, obj=None):
        # if this is not a new object
        if obj:
            return ['uid', 'name', 'former_names', 'date_last_checked']
        else:
            return ['uid', 'former_names', 'date_last_checked']

admin.site.register(m.TwitterUser, TwitterUserAdmin)


class TwitterUserItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'twitter_user', 'date_published', 'twitter_id']
    list_filter = ['date_published']
    search_fields = ['twitter_id', 'item_text']
    readonly_fields = ['twitter_id', 'twitter_user', 'date_published',
                       'item_text', 'item_json', 'place', 'source']
admin.site.register(m.TwitterUserItem, TwitterUserItemAdmin)


class DurationSecondsFilter(admin.SimpleListFilter):
    title = 'duration (s)'
    parameter_name = 'duration_seconds'

    def lookups(self, request, model_admin):
        return (
            ('lt-0.25', '<= 0.25'),
            ('0.25-0.5', '0.25 - 0.5'),
            ('0.5-2', '0.5 - 2'),
            ('gt-2', '>= 2'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'lt-0.25':
            return queryset.filter(duration_seconds__lte=0.25)
        if self.value() == '0.25-0.5':
            return queryset.filter(duration_seconds__gt=0.25,
                                   duration_seconds__lte=0.5)
        if self.value() == '0.5-2':
            return queryset.filter(duration_seconds__gt=0.5,
                                   duration_seconds__lte=2)
        if self.value() == 'gt-2':
            return queryset.filter(duration_seconds__gt=2)


class TwitterUserItemUrlAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'final_status', 'duration_seconds',
                    'expanded_url', 'final_url']
    list_filter = ['date_checked', 'final_status', DurationSecondsFilter]
    search_fields = ['id', 'start_url', 'expanded_url', 'final_url']
    readonly_fields = ['item']
admin.site.register(m.TwitterUserItemUrl, TwitterUserItemUrlAdmin)


class TwitterUserSetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'notes']
    search_fields = ['user', 'name']
admin.site.register(m.TwitterUserSet, TwitterUserSetAdmin)


class TwitterUserTimelineJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_started', 'date_finished', 'num_added']
    list_filter = ['date_started']
    search_fields = ['id']
    readonly_fields = ['date_started', 'date_finished', 'num_added']
admin.site.register(m.TwitterUserTimelineJob, TwitterUserTimelineJobAdmin)


class TwitterUserTimelineErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'user', 'error']
    search_fields = ['job', 'user']
    readonly_fields = ['job', 'user', 'error']
admin.site.register(m.TwitterUserTimelineError, TwitterUserTimelineErrorAdmin)
