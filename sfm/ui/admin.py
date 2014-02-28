from django.contrib import admin

from ui import models as m


class TwitterFilterAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'words', 'people', 'locations']
    list_filter = ['is_active']
    search_fields = ['words', 'people']
admin.site.register(m.TwitterFilter, TwitterFilterAdmin)


class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'uid', 'name', 'former_names',
                    'date_last_checked']
    list_filter = ['is_active']
    search_fields = ['name', 'former_names', 'uid']
    readonly_fields = ['uid', 'former_names', 'date_last_checked']
    filter_horizontal = ['sets']
admin.site.register(m.TwitterUser, TwitterUserAdmin)


class TwitterUserItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'twitter_user', 'date_published', 'twitter_id']
    list_filter = ['date_published']
    search_fields = ['twitter_id', 'item_text']
    readonly_fields = ['twitter_id', 'twitter_user', 'date_published',
                       'item_text', 'item_json', 'place', 'source']
admin.site.register(m.TwitterUserItem, TwitterUserItemAdmin)


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
