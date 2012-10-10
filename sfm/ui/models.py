import gzip
import re
import time

import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models as m
from django.utils import simplejson as json

RE_LINKS = re.compile(r'(https?://\S+)')
RE_MENTIONS = re.compile(u'(@[a-zA-z0-9_]+)')
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
        for line in self.stream:
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
    twitter_user = m.ForeignKey(TwitterUser, related_name='items')
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

    @property
    def tweet(self):
        """Cache/return a parsed version of the json if available."""
        try: 
            return self._parsed_tweet
        except:
            if self.item_json:
                self._parsed_tweet = json.loads(self.item_json)
            else:
                self._parsed_tweet = {}
            return self._parsed_tweet

    @property
    def text(self):
        try:
            return self.tweet['text']
        except:
            return self.item_text

    @property
    def mentions(self):
        return RE_MENTIONS.findall(self.text)

    @property
    def links(self):
        return RE_LINKS.findall(self.text)

    def unshorten(self, url):
        """Don't try to guess; just resolve it, and follow 301s"""
        stack = [url]
        h = requests.head(url)
        while h.status_code == 301:
            location = h.headers['location']
            stack.append(location)
            h = requests.head(location)
        return stack



class Rule(m.Model):
    user = m.ForeignKey(User)
    name = m.CharField(max_length=255, unique=True)
    is_active = m.BooleanField(default=False)
    people = m.TextField(blank=True)
    words = m.TextField(blank=True)
    locations = m.TextField(blank=True)

    def __unicode__(self):
        return '%s' % self.id
