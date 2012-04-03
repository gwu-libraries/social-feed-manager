social feed manager
===================

A django application for managing multiple feeds of social media data.

Developed at the GWU Libraries in Washington, DC, USA.

See also LICENSE.txt.


installation
------------

Developed using python 2.7 and postgresql-9.1 on osx for deployment
on ubuntu lts; your mileage may vary.

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

* specify the location of your virtualenv's site-packages in sfm/wsgi.py

* set up the db from django

        % syncdb

* to plug in to apache, use sfm/apache.conf and adjust in an 
  /etc/apache/sites-available file as appropriate

* start a feed in Gnip's console


usage
-----

* see your rules
    
        % ./manage.py rulesall

* add rules

        % ./manage.py rulesadd foo bar baz
        % ./manage.py rulesadd --tag election2008 obama biden mccain palin

* delete rules

        % ./manage.py rulesdelete foo baz
        % ./manage.py rulesdelete --tag election2008 biden palin

* fetch daily or weekly trends

        % ./manage.py trendsdaily
        % ./manage.py trendsweekly

* watch the stream

        % ./manage.py streamfeed

* poll and save the feed

        % ./manage.py pollfeed --save 

* process saved files into the db

        % ./manage.py processfeed

* run the UI to browse saved data or use the admin

        % ./manage.py runserver
