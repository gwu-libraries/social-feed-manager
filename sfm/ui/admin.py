from django.contrib import admin

from ui import models as m

class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_published', 'rule_tag', 'rule_match',
        'summary']
    list_filter = ['date_published', 'rule_tag', 'rule_match']
    search_fields = ['content']
admin.site.register(m.Status, StatusAdmin)

class RuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'words', 'people', 'locations']
    list_filter = ['is_active']
    search_fields = ['words', 'people']
admin.site.register(m.Rule, RuleAdmin)

class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
admin.site.register(m.TwitterUser, TwitterUserAdmin)

class TwitterUserItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'twitter_user', 'date_published', 'source']
    list_filter = ['date_published', 'source']
    search_fields = ['item_text']
admin.site.register(m.TwitterUserItem, TwitterUserItemAdmin)
