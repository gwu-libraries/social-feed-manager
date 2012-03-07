import re

from django.db import models as m

RE_TWEET_ID = re.compile(r'.*statuses/([0-9]+)$')
RE_USER_NAME = re.compile(r'http://twitter.com/(.*)$')

class Status(m.Model):
    user_id = m.URLField(verify_exists=False)
    date_published = m.DateTimeField()
    avatar_url = m.TextField()
    status_id = m.URLField(verify_exists=False)
    summary = m.TextField()
    content = m.TextField() 
    rule_tag = m.TextField(db_index=True)
    rule_match = m.TextField(db_index=True)
    
    def __unicode__(self):
        return self.status_id

    class Meta:
        ordering = ['date_published']
        verbose_name_plural = 'statuses'

    @property
    def tweet_id(self):
        try:
            m = RE_TWEET_ID.match(self.status_id)
            return m.groups()[0]
        except:
            return 0

    @property
    def user_name(self):
        try:
            m = RE_USER_NAME.match(self.user_id)
            return m.groups()[0]
        except:
            return None
