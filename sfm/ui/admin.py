from django.contrib import admin

from ui import models as m

class RuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'words', 'people', 'locations']
    list_filter = ['is_active']
    search_fields = ['words', 'people']
admin.site.register(m.Rule, RuleAdmin)

class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date_last_checked']
    search_fields = ['name']
admin.site.register(m.TwitterUser, TwitterUserAdmin)

class TwitterUserItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'twitter_user', 'date_published', 'twitter_id']
    list_filter = ['date_published']
    search_fields = ['twitter_id', 'item_text']
admin.site.register(m.TwitterUserItem, TwitterUserItemAdmin)
