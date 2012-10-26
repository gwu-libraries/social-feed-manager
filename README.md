social feed manager
===================

A django application for managing multiple feeds of social media data.

Developed at the GWU Libraries in Washington, DC, USA.

See also LICENSE.txt.


installation
------------

Developed using python 2.7 and postgresql-9.1 on osx for deployment
on ubuntu lts 10.4; your mileage may vary.

* get this code:

        % git clone git://github.com/gwu-libraries/social-feed-manager.git
        % cd social-feed-manager

* create and activate a virtualenv:
  
        % virtualenv --no-site-packages ENV
        % source ENV/bin/activate
    
* install ubuntu package dependencies:
        
        % sudo apt-get install apache2 python-dev postgresql libxml2-dev libxslt1-dev libpq-dev libapache2-mod-wsgi

* prep postgres (change name/pass/permissions/pg_hba.conf as appropriate):
    
        % sudo su - postgres
        (postgres)% psql
        postgres=# create user sfmuser with createdb password 'sfmpass';
        CREATE ROLE
        postgres=# \q
        (postgres)% exit
        % createdb -U sfmuser sfm -W
        Password: <'sfmpass'>

* install requirements

        % pip install -r requirements.txt

* add and edit local_settings.py; include db settings as appropriate

        % cp sfm/local_settings.py.template sfm/local_settings.py

* been moving to twitter's 1.1 api which requires oauth for everything, so
you might find the TWITTER_* settings in flux.  once the UI is running 
after a few more steps, log in to the UI function that requests your 
authentication through Twitter's oauth service.  this will give you a saved
User that you can specify as a TWITTER_DEFAULT_USERNAME which some of the
sample commands down below will use.

* add and edit wsgi.py; specify your virtualenv root as ENV if you use one

        % cp sfm/wsgi.py.template sfm/wsgi.py

* set up the db from django

        % syncdb

* to plug in to apache, use sfm/apache.conf and adjust in an 
  /etc/apache/sites-available file as appropriate


usage
-----

* fetch daily or weekly trends

        % ./manage.py trendsdaily
        % ./manage.py trendsweekly

* log in to the admin app at /admin and add one or more TwitterUsers
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

* run the UI to browse saved data or use the admin

        % ./manage.py runserver

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
