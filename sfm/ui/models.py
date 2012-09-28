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


class TwitterUser(m.Model):
    name = m.TextField(db_index=True)

    def __unicode__(self):
        return 'user %s (sfm id %s)' % (self.name, self.id)

    @property
    def feed_url(self):
        return 'http://api.twitter.com/1/statuses/user_timeline.rss?screen_name=%s' % self.name


class TwitterUserItem(m.Model):
    twitter_user = m.ForeignKey(TwitterUser)
    twitter_url = m.URLField(verify_exists=False, unique=True)
    date_published = m.DateTimeField(db_index=True)
    item_text = m.TextField(default='', blank=True)
    item_json = m.TextField(default='', blank=True)
    place = m.TextField(default='', blank=True)
    source = m.TextField(default='', blank=True)

    def __unicode__(self):
        return 'useritem (%s) %s' % (self.id, self.twitter_url)

    @property
    def tweet_id(self):
        try:
            m = RE_TWEET_ID.match(self.twitter_url)
            return m.groups()[0]
        except:
            return 0

    @property
    def tweet_json_url(self):
        return 'http://api.twitter.com/1/statuses/show/%s.json' % self.tweet_id 


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
        return '%s' % self.status_id

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


class Rule(m.Model):
    name = m.CharField(max_length=255, unique=True)
    is_active = m.BooleanField(default=False)
    people = m.TextField(blank=True)
    words = m.TextField(blank=True)
    locations = m.TextField(blank=True)

    def __unicode__(self):
        return '%s' % self.id
