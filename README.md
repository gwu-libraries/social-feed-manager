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
    

* install requirements

        % pip install -r requirements.txt

* add and edit local_settings.py

        % cp sfm/local_settings.py.template sfm/local_settings.py

* create local database as you specified in local_settings.py

        % createdb yourdbname

* set up the db from django

        % syncdb

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

* watch the stream

        % ./manage.py streamfeed

* poll and save the feed

        % ./manage.py pollfeed --save 

* process saved files into the db

        % ./manage.py processfeed
