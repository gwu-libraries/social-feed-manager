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
        
        % sudo apt-get install git apache2 python-dev python-virtualenv postgresql libxml2-dev libxslt1-dev libpq-dev libapache2-mod-wsgi supervisor

* get this code:

        % git clone git://github.com/gwu-libraries/social-feed-manager.git
        % cd social-feed-manager

* create and activate a virtualenv:
  
        % virtualenv --no-site-packages ENV
        % source ENV/bin/activate
    
* prep postgres: first, update /etc/postgresql/9.1/main/pg_hba.conf to
enable local database connections or otherwise as you prefer.  note: 
there's more than one way to do this, so if this is new to you, read this,
or ask a friendly sysadmin for help:

        http://www.postgresql.org/docs/9.1/static/auth-pg-hba-conf.html

        For example, you could add a line like this:

        ```local   all             all                     md5```

        Restart postgres when this is done.

        % sudo service postgresql restart
    
* su to the ```postgres``` account to create a postgresql user and database:
    
        % sudo su - postgres
        (postgres)% psql
        postgres=# create user YOURSFMDBUSERNAME with createdb password 'YOURSFMDBPASSWORD';
        CREATE ROLE
        postgres=# \q
        (postgres)% createdb -O YOURSFMDBUSERNAME sfm -W
        Password: YOURSFMDBPASSWORD
        (postgres)% (ctrl-d to log out of postgres acct)

* install requirements

        % pip install -r requirements.txt

* add and edit local_settings.py; include db settings and define
ALLOWED_HOSTS as appropriate

        % cd sfm
        
* note that at this point you should have an ```sfm``` directory 
inside another ```sfm``` directory - the settings files are in this
second-level sfm directory:

        % cp sfm/local_settings.py.template sfm/local_settings.py

* edit ```sfm/local_settings.py``` to set TWITTER_DEFAULT_USERNAME
to the twitter account username that you would like the application to use
to register other users.

* Using the twitter account you designated as your TWITTER_DEFAULT_USERNAME,
log in to:


        https://dev.twitter.com/apps/new

    Then create an app for your instance of SFM.  In addition to
    the required values, set the application type to "read only",
    and give it a callback URL.  The callback URL can be the same as
    your website URL, but you have to provide a value or the authorization
    loop between twitter/oauth and django-social-auth/ sfm will not work
    correctly.

    Use the resulting OAuth settings' consumer key and secret as your
    TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET in local_settings.py.

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

* Make sure you are logged out of twitter in your browser.  Use the "log in"
link on your SFM app's home page.  The login page requests your authentication
through Twitter's OAuth service.  Log in using the twitter account you
specified earlier as your TWITTER_DEFAULT_USERNAME.  This will give you a
saved django User and associated User Social Auth for the
TWITTER_DEFAULT_USERNAME which some of the commands down below will use.

* log in to the admin app at /admin using the superuser django prompted
you to create when you ran "syncdb" above.  add one or more TwitterUsers
(use real screen names), then you can fetch the most recent 3200 tweets
for each.

        % ./manage.py user_timeline

* this works as a cronjob, e.g. to run it every two hours, if you installed
it under /sfm (spells out virtualenv-based paths, adjust as necessary):

        5 */2 * * * cd /sfm/social-feed-manager && /sfm/social-feed-manager/ENV/bin/python /sfm/social-feed-manager/sfm/manage.py user_timeline

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


optional setup for supervised streamsample (Twitter sample/spritzer feed)
--------------------------------------------------------------

If you want to capture sample data from Twitter's spritzer feed
continually, you might want a process supervisor to ensure the process
remains active and is restarted automatically after system reboots and
the like.  ```supervisor``` does that for sfm.  These steps will get
you started.  

*NOTE*:  The sample stream includes something like 0.5-1% of all tweets
and deletes, which as of February 2014 means roughly three million
or so items combined.  These files will add up quickly, so consider
your available disk space, and consider using the ```organizedata```
management command in a cron job to sort generated files into date-based
directories regularly.

* edit /etc/supervisor/supervisord.conf and add supervisor.d/*.conf
  to the [include] files.  Use a space to separate it from the existing value
  of ```files``` by a space:

       files = /etc/supervisor/conf.d/*.conf <PATH_TO_YOUR_SFM>/sfm/sfm/supervisor.d/*.conf

* create a /var/log/sfm directory.  The supervisor-supervised processes will
  write log files to this directory.

        % sudo mkdir /var/log/sfm

* edit local_settings.py to set DATA_DIR to the directory where you want
  streamsample output stored.  Set SUPERVISOR_PROCESS_OWNER to a user who
  has rights to write to /var/log/sfm.  You may optionally wish to adjust 
  SAVE_INTERVAL_SETTINGS, which controls how often sfm will save data.

* set the permissions on the sfm/sfm/supervisor.d directory to allow the
  sfm process owner to write to it.  Since the sfm process may be running
  as a different user than the owner of the directory, we're going to create
  a new 'sfm' group:

        % sudo groupadd sfm

  and add the sfm process owner to this group.  Edit /etc/group:
  
        % sudo vi /etc/group
        
  You should see a new line at the end that looks something like this:
  
        sfm:x:<a group number>:

  Add the process owner, and optionally add your own user to this group:
  
        sfm:x:<a group number>:www-data,<your user name>

  Now change the group of the supervisor.d directory to sfm:

        % sudo chgrp sfm sfm/sfm/supervisor.d

* copy supervisor.d/streamsample.conf.template to supervisor.d/streamsample.conf 

        % cd sfm/sfm/supervisor.d
        % cp streamsample.conf.template streamsample.conf

  and edit streamsample.conf  to use the path to your sfm project, the value
  of the PATH environment variable set within your virtualenv, and to use your
  preferred system user account (to avoid having the output files owned by
  root).

* to verify that supervisord detected the new configuration file and
  started the process, run supervisorctl:

        % sudo supervisorctl

* if you don't see a line that reads something like:

        streamsample                     RUNNING    pid 889, uptime 21:45:25

  then at the supervisor prompt, run 'update' to reload the config files:

        supervisor> update

  and start streamsample

        supervisor> start streamsample

Supervisor can also be used to manage filterstream processes.  As you [create/modify and] activate TwitterFilters using the admin UI, SFM creates a supervisor configuration file for each TwitterFilter.  It will also delete a configuration file when you mark a TwitterFilter as inactive.

However, if you have pre-existing, active TwitterFilters which were created prior to SFM release m4_001, you will need to run the ```createconf``` command to create supervisor configuration files for your active TwitterFilters.

* With your virtualenv activated (see above), execute:

        % ./manage.py createconf

* IMPORTANT: Currently supervisor does not appear to automatically detect 
  additions/deletions/changes to the filterstream configuration files that occur
  when you run createconf and/or make changes to TwitterFilter.  To "refresh"
  supervisor, execute:

        % sudo supervisorctl update


development
-----------

To work on sfm, clone/fork it in github.  If you send pull requests from
a fork, please make them as atomic as you can.

We are actively working on this, making changes in response to university
researcher requests.  If the features it supports seem fickle and spotty
it's because we're still just getting started and still figuring out
what we need it to do.  Please get in touch and tell us what you think.
