from django.contrib import admin

from ui import models as m

class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_published', 'rule_tag', 'rule_match',
        'summary']
    list_filter = ['date_published', 'rule_tag', 'rule_match']
    search_fields = ['content']
admin.site.register(m.Status, StatusAdmin)
