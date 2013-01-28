import datetime
import gzip
import re
import time

import requests
import tweepy
from tweepy.parsers import JSONParser
from tweepy.streaming import StreamListener

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models as m
from django.utils import simplejson as json
from django.utils import timezone

RE_LINKS = re.compile(r'(https?://\S+)')
RE_MENTIONS = re.compile(u'(@[a-zA-z0-9_]+)')
RE_TWEET_ID = re.compile(r'.*statuses/([0-9]+)$')
RE_USER_NAME = re.compile(r'http://twitter.com/(.*)$')

DAY = datetime.timedelta(days=1)
dt = datetime.datetime(2012, 1, 1)
dt_end = datetime.datetime.today()
DATES = []
while dt < dt_end:
    DATES.append(dt)
    dt += DAY


def authenticated_api(username, api_root=None, parser=None):
    """Return an oauthenticated tweety API object."""
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, 
            settings.TWITTER_CONSUMER_SECRET)
    try:
        user = User.objects.get(username=username)
        sa = user.social_auth.all()[0]
        auth.set_access_token(sa.tokens['oauth_token'], 
                sa.tokens['oauth_token_secret'])
        return tweepy.API(auth, 
                api_root=api_root or settings.TWITTER_API_ROOT, 
                parser=parser or JSONParser(),
                secure=settings.TWITTER_USE_SECURE) 
    except:
        return None


def dt_aware_from_created_at(created_at):
    ts = time.mktime(time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y'))
    dt = datetime.datetime.fromtimestamp(ts)
    return timezone.make_aware(dt, timezone.utc)


class RotatingFile(StreamListener):

    def __init__(self, filename_prefix='data', 
            save_interval_seconds=0, data_dir='', compress=True):
        self.filename_prefix = filename_prefix
        self.save_interval_seconds = save_interval_seconds \
                or settings.SAVE_INTERVAL_SECONDS
        self.data_dir = data_dir or settings.DATA_DIR
        self.compress = compress
        self.start_time = time.time()
        self.fp = self._get_file()

    def on_data(self, data):
        self.fp.write('%s\n' % data)
        time_now = time.time()
        if time_now - self.start_time > self.save_interval_seconds:
            self.fp.close()
            self.fp = self._get_file()
            self.start_time = time_now

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
    date_last_checked = m.DateTimeField(db_index=True, auto_now=True)
    is_active = m.BooleanField(default=True)

    def __unicode__(self):
        return 'user %s (sfm id %s)' % (self.name, self.id)

    @property
    def feed_url(self):
        return 'http://api.twitter.com/1/statuses/user_timeline.rss?screen_name=%s' % self.name

    @property
    def counts(self):
        return ','.join([str(dc.num_tweets) for dc in self.daily_counts.all()])


class TwitterUserItem(m.Model):
    twitter_user = m.ForeignKey(TwitterUser, related_name='items')
    twitter_id = m.BigIntegerField(unique=True, default=0)
    date_published = m.DateTimeField(db_index=True)
    item_text = m.TextField(default='', blank=True)
    item_json = m.TextField(default='', blank=True)
    place = m.TextField(default='', blank=True)
    source = m.TextField(default='', blank=True)

    def __unicode__(self):
        return 'useritem (%s) %s' % (self.id, self.twitter_id)

    @property 
    def twitter_url(self):
        return 'http://twitter.com/%s/status/%s' % (self.twitter_user.name,
                self.twitter_id)

    @property
    def tweet_json_url(self):
        """Note: hard-codes v1 api in URL; will break in March 2013.
        v1.1 requires oauth request."""
        return 'http://api.twitter.com/1/statuses/show/%s.json' % self.twitter_id 

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
        h = requests.head(url)
        stack = [i.url for i in h.history]
        stack.append(h.url)
        return stack

    @property
    def csv(self):
        """A list of values suitable for csv-ification"""
        return [
            str(self.id), 
            datetime.datetime.strftime(self.date_published, 
                '%Y-%m-%dT%H:%M:%SZ'),
            self.tweet['id_str'], 
            self.tweet['user']['screen_name'],
            str(self.tweet['user']['followers_count']),
            str(self.tweet['user']['friends_count']),
            str(self.tweet['retweet_count']),
            ', '.join([ht['text'] \
                for ht in self.tweet['entities']['hashtags']]),
            self.tweet['in_reply_to_screen_name'] or '',
            ', '.join([m for m in self.mentions]),
            self.twitter_url,
            self.tweet['text'],
            ]


class Rule(m.Model):
    user = m.ForeignKey(User)
    name = m.CharField(max_length=255, unique=True)
    is_active = m.BooleanField(default=False)
    people = m.TextField(blank=True)
    words = m.TextField(blank=True)
    locations = m.TextField(blank=True)

    def __unicode__(self):
        return '%s' % self.id


class DailyTwitterUserItemCount(m.Model):
    twitter_user = m.ForeignKey(TwitterUser, related_name='daily_counts')
    date = m.DateField(db_index=True, blank=True)
    num_tweets = m.IntegerField(default=0)

    def __unicode__(self):
        return '%s' % self.id

    class Meta:
        ordering = ['date']
