social feed manager
===================

A django application for managing multiple feeds of social media data.

Developed at the GWU Libraries in Washington, DC, USA.

See also LICENSE.txt.


installation
------------

Developed using python 2.7 and postgresql-9.1 with and for deployment
on ubuntu lts 12.04; your mileage may vary.

* install ubuntu package dependencies:
        
        % sudo apt-get install git apache2 python-dev python-virtualenv postgresql libxml2-dev libxslt1-dev libpq-dev libapache2-mod-wsgi

* get this code:

        % git clone git://github.com/gwu-libraries/social-feed-manager.git
        % cd social-feed-manager

* create and activate a virtualenv:
  
        % virtualenv --no-site-packages ENV
        % source ENV/bin/activate
    
* prep postgres (change name/pass/permissions/pg_hba.conf as appropriate, and pick your own user/passwd):
    
        % sudo su - postgres
        (postgres)% psql
        postgres=# create user YOURSFMDBUSERNAME with createdb password 'YOURSFMDBPASSWORD';
        CREATE ROLE
        postgres=# \q
        (postgres)% createdb -U YOURSFMDBUSERNAME sfm -W
        Password: YOURSFMDBPASSWORD

* install requirements

        % pip install -r requirements.txt

* add and edit local_settings.py; include db settings and define
ALLOWED_HOSTS as appropriate

        % cd sfm
        % cp sfm/local_settings.py.template sfm/local_settings.py

* you might find the TWITTER_* settings in flux, but at minimum you will
need to use an existing twitter account to register other users.  use that
account to log in at:

        https://dev.twitter.com/apps/new

    Then create an app.  In addition to the required values, set
    the application type to "read only", and give it a callback URL.
    This can be the same as your website URL, but you have to provide
    a value or the authorization loop between twitter/oauth and
    django-social-auth/ sfm will not work correctly.  Use the resulting
    OAuth settings' consumer key and secret as your TWITTER_CONSUMER_KEY
    and TWITTER_CONSUMER_SECRET.

* once the sfm UI is running (after a few more steps), log in to the
UI function that requests your authentication through Twitter's oauth
service.  this will give you a saved User that you can specify as a
TWITTER_DEFAULT_USERNAME which some of the commands down below will use.
Set this username as TWITTER_DEFAULT_USERNAME in your local_settings.py.

* to verify, you should have each of these set in ```local_settings.py```:

```python
TWITTER_DEFAULT_USERNAME 
TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET
```

* add and edit wsgi.py; specify your virtualenv root as ENV if you use one

        % cp sfm/wsgi.py.template sfm/wsgi.py

* set up the db from django

        % ./manage.py syncdb

    This will prompt you to create a superuser for administrating the
    running app.  Create one and remember your account info.

* run migrations for social_auth and ui

        % ./manage.py migrate

* to plug in to apache, use sfm/apache.conf and adjust in an 
  /etc/apache/sites-available file as appropriate

* if you are upgrading a database that was created in m1_001,
  run populate_uids to add user ids to TwitterUser nicks:

        % ./manage.py populate_uids


usage
-----

* run the UI to browse saved data and use the admin:

        % ./manage.py runserver

* the home page will be at '/', the admin app at '/admin'. exciting eh.

* log in to the admin app at /admin using the superuser django prompted
you to create when you ran "syncdb" above.  add one or more TwitterUsers
(use real screen names), then you can fetch the most recent 3200 tweets
for each.

        % ./manage.py user_timeline

* this works as a cronjob, e.g. to run it every two hours, if you installed
it under /sfm (spells out virtualenv-based paths, adjust as necessary):

        5 */2 * * * cd /sfm/social-feed-manager && /sfm/social-feed-manager/ENV/bin/python /sfm/social-feed-manager/sfm/manage.py user_timeline

* once you fetch one or more user timelines, you can pre-process the
data that the home page sparklines with "dailycounts", which you could run as
a nightly cronjob like the above, or from the commandline:

        % ./manage.py dailycounts

* fetch daily or weekly trends

        % ./manage.py trendsdaily
        % ./manage.py trendsweekly

* use the admin UI to add a Rule, which specifies follow, track, or locations
to use to poll from twitter's statuses/filter function. then you can poll
with the filterstream command, which will write out gzipped files at intervals
you can specify:

        % ./manage.py filterstream

* to tidy up a bunch of those files into data directories named and organized
by stream type and date:

        % ./manage.py organizedata

* to grab the statuses/sample stream:

        % ./manage.py streamsample

Note that if you're going to be using twitter's streams, you should be 
familiar with their documentation:

    https://dev.twitter.com/docs/streaming-apis



development
-----------

To work on sfm, clone/fork it in github.  If you send pull requests from
a fork, please make them as atomic as you can.

We are actively working on this, making changes in response to university
researcher requests.  If the features it supports seem fickle and spotty
it's because we're still just getting started and still figuring out
what we need it to do.  Please get in touch and tell us what you think.
