import gzip
import re
import time

from django.conf import settings
from django.db import models as m

RE_TWEET_ID = re.compile(r'.*statuses/([0-9]+)$')
RE_USER_NAME = re.compile(r'http://twitter.com/(.*)$')


class RotatingFile(object):

    def __init__(self, stream, filename_prefix='data',
            save_interval_seconds=0, data_dir='', compress=True):
        self.stream = stream
        self.filename_prefix = filename_prefix
        self.save_interval_seconds = save_interval_seconds \
                or settings.SAVE_INTERVAL_SECONDS
        self.data_dir = data_dir or settings.DATA_DIR
        self.compress = compress

    def handle(self):
        start_time = time.time()
        fp = self._get_file()
        for line in self.stream.iter_lines():
            if line:
                fp.write('%s\n' % line)
                time_now = time.time()
                if time_now - start_time > self.save_interval_seconds:
                    fp.close()
                    fp = self._get_file()
                    start_time = time_now

    def _get_file(self):
        if self.compress: 
            return gzip.open(self._get_filename(), 'wb')
        else:
            return open(self._get_filename(), 'wb')

    def _get_filename(self):
        return '%s/%s-%s%s' % (self.data_dir, self.filename_prefix,
                time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                '.gz' if self.compress else '')


class TrendWeekly(m.Model):
    date = m.DateField(db_index=True)
    events = m.TextField(blank=True)
    name = m.TextField(db_index=True)
    promoted_content = m.TextField(blank=True)
    query = m.TextField()

    def __unicode__(self):
        return '%s - %s (%s)' % (self.name, self.date, self.id)

    class Meta:
        ordering = ['-date', 'name']
        verbose_name_plural = 'trendsweekly'


class TrendDaily(m.Model):
    date = m.DateTimeField(db_index=True)
    events = m.TextField(blank=True)
    name = m.TextField(db_index=True)
    promoted_content = m.TextField(blank=True)
    query = m.TextField()

    def __unicode__(self):
        return '%s - %s (%s)' % (self.name, self.date, self.id)

    class Meta:
        ordering = ['-date', 'name']
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


