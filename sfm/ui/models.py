from django.db import models as m

class Status(m.Model):
    user_id = m.URLField(verify_exists=False)
    date_published = m.DateTimeField()
    avatar_url = m.TextField()
    status_id = m.URLField(verify_exists=False)
    summary = m.TextField()
    content = m.TextField() 
    rule_tag = m.TextField(db_index=True)
    rule_match = m.TextField(db_index=True)
    
    class Meta:
        verbose_name_plural = 'statuses'
