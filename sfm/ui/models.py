import re

from django.db import models as m

RE_TWEET_ID = re.compile(r'.*statuses/([0-9]+)$')
RE_USER_NAME = re.compile(r'http://twitter.com/(.*)$')


class TrendWeekly(m.Model):
    date = m.DateField(db_index=True)
    events = m.TextField(blank=True)
    name = m.TextField(db_index=True)
    promoted_content = m.TextField(blank=True)
    query = m.TextField()
    sequence_num = m.SmallIntegerField(default=1)

    def __unicode__(self):
        return '%s - %s (%s)' % (self.name, self.date, self.sequence_num)

    class Meta:
        ordering = ['-date', 'sequence_num']
        verbose_name_plural = 'trendsweekly'


class TrendDaily(m.Model):
    date = m.DateTimeField(db_index=True)
    events = m.TextField(blank=True)
    name = m.TextField(db_index=True)
    promoted_content = m.TextField(blank=True)
    query = m.TextField()
    sequence_num = m.SmallIntegerField(default=1)

    def __unicode__(self):
        return '%s - %s (%s)' % (self.name, self.date, self.sequence_num)

    class Meta:
        ordering = ['-date', 'sequence_num']
        verbose_name_plural = 'trendsdaily'


class Status(m.Model):
    user_id = m.URLField(verify_exists=False)
    date_published = m.DateTimeField(db_index=True)
    avatar_url = m.TextField()
    status_id = m.URLField(verify_exists=False)
    summary = m.TextField()
    content = m.TextField() 
    rule_tag = m.TextField(db_index=True)
    rule_match = m.TextField(db_index=True)
    
    def __unicode__(self):
        return self.status_id

    class Meta:
        ordering = ['-date_published']
        verbose_name_plural = 'statuses'

    @property
    def tweet_id(self):
        try:
            m = RE_TWEET_ID.match(self.status_id)
            return m.groups()[0]
        except:
            return 0

    @property
    def tweet_json_url(self):
        return 'http://api.twitter.com/1/statuses/show/%s.json' % self.tweet_id 

    @property
    def user_name(self):
        try:
            m = RE_USER_NAME.match(self.user_id)
            return m.groups()[0]
        except:
            return None


