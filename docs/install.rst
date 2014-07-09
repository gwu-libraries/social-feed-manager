.. Social Feed Manager Installation and Configuration

Installation and Configuration
==============================

Background
----------

Social Feed Manager is not a simple "click to run" application.
It is best if you or somebody you can work with has some experience
as a unix/linux systems administrator when attempting to install this
application.  It's not the world's most complicated app, but you will
need to install system software and configure it, set up a database,
get application credentials from Twitter, and then use all of that to
configure and run SFM, which is a python/django application that plugs
into a web server.  If these are new tasks for you, you might want to
work with another person with a little more experience.

Another key consideration is platform.  At GW Libraries we develop,
test, and run SFM strictly on Ubuntu LTS servers (virtual machines,
actually), so these docs reflect that.  If you want to install SFM into
another environment you will be on your own to some degree.  But if you
stick with Ubuntu LTS (currently 12.04) these instructions should work
for you if you follow them precisely.

We develop and run SFM inside a virtualenv, which is a commonly used
sandbox / isolation technique for Python applications.  This allows
a Python application and its third-party library dependencies to
be installed into one independent virtual environment for the app
side-by-side with other applications (and perhaps their own virtualenvs)
on the same system, or even alongside multiple versions of SFM itself.
There are many benefits to using virtualenv for this purpose.  We strongly
recommend that you do the same, and these instructions will guide you.


Dependencies
------------

These instructions assume you have a brand new Ubuntu 12.04 LTS server.

SFM is developed and managed using Ubuntu 12.04, Python 2.7, PostgreSQL
9.1+, Apache 2+, and other dependencies we'll run into in a moment.
If you want to use something else, you're on your own, but let us know and
please feel welcome to submit a pull request with your own suggestions.

First, install these system-level packages:

::

    % sudo apt-get install git apache2 python-dev python-virtualenv postgresql libxml2-dev libxslt1-dev libpq-dev libapache2-mod-wsgi supervisor

Next, get this code using git:

::

    % git clone https://github.com/gwu-libraries/social-feed-manager.git
    % cd social-feed-manager

Create and activate a virtualenv:

::

    % virtualenv --no-site-packages ENV
    % source ENV/bin/activate

Note that the first command creates a virtualenv, and the second command
activates it.  For nearly all of the following instructions, we assume
you are active in the virtualenv you just created.

Prep PostgreSQL, the database SFM uses.  First, update
``/etc/postgresql/9.1/main/pg_hba.conf`` to enable local database
connections or otherwise as you prefer.  Note that there's more than
one way to do this, so if this is new to you, read this background
information, or ask a friendly sysadmin for help.

::

  http://www.postgresql.org/docs/9.1/static/auth-pg-hba-conf.html

For example, you could add a line like this (you will probably need
to use ``sudo`` to edit the file):

::

   local   all             all                     md5

When you've edited ``pg_hba.conf``, save it, then restart postgresql.

::

    % sudo service postgresql restart

When that succeeds, su to the ``postgres`` account to create a postgresql
user and database.  Substitute your own preferred values for the all caps
values below, but do use the single quotes around your password when you
create it in the third line.

:: 

    % sudo su - postgres
    (postgres)% psql
    postgres=# create user YOURSFMDBUSERNAME with createdb password 'YOURSFMDBPASSWORD';
    CREATE ROLE
    postgres=# \q
    (postgres)% createdb -O YOURSFMDBUSERNAME sfm -W
    Password: YOURSFMDBPASSWORD
    (postgres)% (ctrl-d to log out of postgres acct)

Now install the python library requirements in your virtualenv using
``pip``.  This might take a few minutes.  This step requires that you
successfully installed all of the system-level packages above.  Note that
these python packages are being installed into your virtualenv, not
system-wide, which is what we want.  They will only be available while
you are in this activated virtualenv.

::

    % pip install -r requirements.txt

That should be everything you have to install.  Now it's on to configuring
the SFM app itself.  Progress!


Configuration
-------------

Now we'll configure the SFM app itself. Before we do, though, did you go
through all of the steps above?  If not, or if you're using a different
platform, you might have different results.  So now's a good time to check
that each of these tasks is done:

- installed system-level dependencies using apt-get install
- cloned the social-feed-manager repo using git
- activated the virtualenv sandbox for your sfm setup
- configured postgresql, restarted it, created a db and a user
- installed app-level dependencies in the sfm virtualenv using pip 

If you haven't done all of these, please go back and be sure you do.

Next we configure the SFM app, which takes a few steps:

- set configuration parameters for SFM itself
- obtain Twitter API credentials and specify them in the SFM config
- set up the database

If you aren't already there, cd into the social-feed-manager/sfm directory
first:

::

    % cd sfm

Django uses a ``settings.py`` file for most configurations; SFM also uses
a second ``local_settings.py`` file for installation details like database
name and user and Twitter API authentication information.  We include
a template version of that file in the ``social-feed-manager/sfm/sfm``
directory to make it easy to get started.  You'll copy that to your own
``local_settings.py`` file and edit that to specify your configuration.

Copy the template to your own local settings file:

::

    % cp sfm/local_settings.py.template sfm/local_settings.py

Edit this file and set appropriate values for just these parameters at
first, we'll go back later and get the rest:

- ADMINS (specify your name and email address in the format provided)
- DATABASES (NAME, USER, PASSWORD as you defined for postgres above)
- DATA_DIR (create a directory to hold data files, then specify it here;
  use a new directory that is not inside the social-feed-manager directory)
- TWITTER_DEFAULT_USER (the name of the twitter account you'll use to
  connect to the API; we'll specify the other TWITTER_* settings in a bit)

Next, do the same for the ``wsgi.py`` file, copy its template to a new
file specific to your installation:

::

    % cp sfm/wsgi.py.template sfm/wsgi.py

In this new file ``wsgi.py``, uncomment just the three lines below the
one that starts with "if using a virtualenv...", then specify the location
of your virtualenv in the second of these lines.  When you're done, it
should look something like this:

::

    import site
    ENV = '/home/dchud/social-feed-manager/ENV'
    site.addsitedir(ENV + '/lib/python2.7/site-packages')

WSGI is a specification for connecting applications like SFM to web
servers; this file tells a web server where to look for the SFM app and
its dependencies on your system.  We'll configure the web server later.

Our next step is critical - register your SFM instance with Twitter's
"Application Management" page.  Log in to Twitter using the account you
specified as ``TWITTER_DEFAULT_USER``, then visit this page:

::

    https://dev.twitter.com/apps/new

Here, create an app for your instance of SFM. In addition to the required
values, set the application type to "read only", and give it a callback
URL. The callback URL can be the same as your website URL, but you have
to provide a value or the authorization loop between twitter/oauth and
django-social-auth/ sfm will not work correctly.

Did you give it a callback URL?  Good.  It's required.  Really.

When you finish this process, you'll see a OAuth consumer key and secret
for your SFM instance.  Use these as the values for these two settings in 
``local_settings.py``:

- TWITTER_CONSUMER_KEY
- TWITTER_CONSUMER_SECRET

These two settings along with ``TWITTER_DEFAULT_USERNAME`` should all
be defined now with real values from your account and your SFM app's
OAuth key/secret.


First time running SFM
----------------------

There are several layers of "users" with SFM; the next steps are critical
because if the users aren't lined up just right, SFM won't be able to
use Twitter's API.  It can be a little confusing, but it's important to
understand what's going on here.

The first few layers of users are at the system-level.  You are logged in
to your machine using a system user; using that account, you installed
system-level dependencies (with sudo or as root, perhaps).  You also
configured PostgreSQL and cloned SFM and installed SFM's dependencies
with the system user.  When you configured PostgreSQL you also created
a user for PostgreSQL.  The PostgreSQL user is what SFM uses to connect to
the PostgreSQL database.

Next, there are two kinds of Twitter users we are interested in.  First,
you used your own Twitter account to register your SFM install with
Twitter; the OAuth keys you received for that user allow SFM to connect
to the Twitter API.  This is separate from the accounts of Twitter users
for which you want to collect tweets, which we'll also record in the
system later, in the database, using SFM.

Finally, to log in and use SFM through the web, there are two kinds of
SFM app-level users.  You can have administrative accounts (we'll create
one in a second), strictly for housekeeping purposes, and you can also
have Twitter-authenticated users for day-to-day use (we'll create one of
these too).  The administrative accounts may be Twitter-authenticated,
but they don't have to be.

This is all very confusing, yes, but it will make more sense in a few
minutes.

The final step before running SFM finally is to "migrate" the database.

::

    % ./manage.py migrate

Now we're ready to run SFM.

First, we set up the database using the regular django method ``syncdb``,
but read the next three paragraphs first, they're important.

``syncdb`` will use the settings you configured in ``local_settings.py``
to connect to the database and set up the tables SFM requires.

This will also ask you to create a superuser.  Do this, and
name it ``sfmadmin``.  Don't name it the same thing as your
``TWITTER_DEFAULT_USER``.  You will be prompted for an email address
and password, fill these in and remember your password.

Did you call the superuser ``sfmadmin``?  Really?  Good.

::

    % ./manage.py syncdb

When that completes, we need to "migrate" the database to the most
recent data model:

::

    % ./manage.py migrate

When that completes, we're ready to run the app, finally:

::

    % ./manage.py runserver

By default, this will run SFM using Python's built-in web server, on
a high port number like 8000.  If you are on a server that doesn't
allow web traffic through port 8000 through the firewall, but does
allow port 8080, you can specify a host and port:

::

    % ./manage.py runserver sfm.example.com:8080

This will start the web application on sfm.example.com at port 8080.

The built-in web server is really only good for development and testing,
not production, but it does provide access to everything the app does.

Next, visit the webapp in your browser: http://sfm.example.com:8080/

You should see a blue bar at the top and a request to "Please log
in" and a button to "Log in with Twitter".  Click that button, and
now log in through Twitter using the account you specified in your
``TWITTER_DEFAULT_USERNAME``.  Maybe your browser is still logged in
with this account because you configured your SFM instance at Twitter
and got your OAuth credentials with it, in which case, great.

If this works, it should bounce you back to your sfm.example.com site
and you should see an empty SFM, with no users listed, but you should
be reassured to see "log out YOURNAME" in the top blue bar.  If that
works, you're in great shape.

Now, click "log out YOURNAME" and log out.  Yes, log back out.

Next, in your browser, then, visit: http://sfm.example.com:8080/admin

You'll see a different user/pass challenge.  Here, enter the SFM
app-level superuser name "sfmadmin" and password you created above
when you ran ``syncdb``.  This should drop you into the admin screen.
Under "Site administration" -> "Auth", click "Users".  You should see
two different app users, one called "sfmadmin" and another with your
``TWITTER_DEFAULT_USERNAME``.  "sfmadmin" should have "Staff status"
with a green checkmark; the other account does not, and has a red circle
with a white minus sign.  If you see all this, you are in good shape.

Next, click on "Home", then under "Social_Auth", click "User social
auths".  On the next screen you should see one user, with your
``TWITTER_DEFAULT_USERNAME``.  Click the number next to its name, and
you'll see the OAuth access token for this user which allows SFM to
connect to the Twitter API.

Why doesn't "sfmadmin" have a social auth?  Because it only ever logged
in to SFM.  The sfmadmin account is only for your housekeeping needs;
the other account can be used to connect and read data from the API.

What's the social auth?  These are credentials that allow your SFM
instance to connect to Twitter's API on behalf of your Twitter account.
sfmadmin never logged in through Twitter, so it doesn't have one, and
it doesn't need one.

If this is still confusing, try this:  log out again, then grab a colleage
and have them log in to your SFM using their own Twitter account (with the
"Log in with Twitter" button on the home page).  After they're done, log
them out of SFM, then log back in using sfmadmin and the ``/admin`` URL.
Under the Auth -> Users list, and in User social auths, you'll see their
new sfm account.  Get the difference now?

The OAuth credentials you got when you registered your SFM instance allow
SFM to connect to the Twitter API to do things like let users log in to
SFM themselves through Twitter.  Then, when you finally do connect to
the Twitter API to get data, you'll use a combination of your app-level
OAuth credentials and the access token for your ``TWITTER_DEFAULT_USER``
or another credentialed user to get that data.

So let's do that now.

Logged in to the ``/admin`` page using your sfmadmin administrative
account, go Home, then under "Ui" click "Twitter users".  There shouldn't
be any yet - these are the names of accounts you want to collect.
At the top right, click "Add twitter user", and on the next screen,
enter the name "bbcnews" (no quotes, though!), which is a good example
because it's active all the time.  At the bottom right, click "Save".

If this succeeds, you should see that user "BBCNews" is now added to
your system as a twitter user.  Note that it's "BBCNews", not "bbcnews"
- when you clicked "Save", SFM did the following:
  
  - connected to Twitter's API using your ``TWITTER_DEFAULT_USER``
    account credentials
  - queried Twitter's API for a user named "bbcnews"
  - found the account "BBCNews" and its info
  - stored this as a new TwitterUser in SFM, using the case-corrected
    name form

If it didn't work, double-check your spelling.

This is the easiest way to add users to SFM.

Now that you've added a TwitterUser, let's fetch its recent tweets.

Back in your terminal window, enter:

::

    % ./manage.py user_timeline

Sit back and watch for a bit.  SFM will connect to Twitter's
API and make a series of calls to fetch 200 recent tweets at a
time, up to 3200 total, pausing between each call.  The numbers
200 and 3200 aren't arbitrary, they are set by Twitter (see
https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline for
details).  SFM abides by Twitter's API and pauses regularly so that it
can stay within the API's rate limits.

You are now up and running with SFM.


Apache integration
------------------

To run SFM in production, we recommend integrating with apache using WSGI.
It's straightforward and well-tested.  You will need to copy a configuration
file into apache's ``sites-available`` directory, edit that file to match
your installation details, enable that site (and optionally disable other
versions), then restart apache.  Let's get started.

First, copy our apache configuration template to ``sites-available``. We
like to append the appname "sfm" with the version number,
e.g. ``sfm_m4_002``, so when we go to deploy a new version, we can just
add a new config file and make the switchover easy.  You could just call
it ``sfm`` if you want, but it can help to have the version number in 
there, so these instructions use that convention.

::

    % sudo cp sfm/apache.conf /etc/apache2/sites-available/sfm_m4_002
    % sudo vim /etc/apache2/sites-available/sfm_m4_002

You will need to change several things in this file:

 - change references to ``/PATH/TO/sfm`` to the full absolute path to 
   your ``social-feed-manager/sfm`` directory
 - change references to ``YOUR-HOSTNAME.HERE`` to your public hostname
 - change the reference to ``/PATH/TO/YOUR/VENV`` to the full absolute
   path to your virtualenv (ending in ``ENV``) which you created above
 - change the reference to ``python/2.X`` to 2.7

When you've made all those changes, save the file.

Next, enable the site configuration you just created:

::

    % sudo a2ensite sfm_m4_002

Assuming you are installing in a clean VM, disable the pre-existing
default site:

::

    % sudo a2dissite 000-default

Reload the apache configuration, as it suggts when you made the changes
above:

::

    % sudo service apache2 reload

That's it!  It should be working now.

If you run into any problems, check the logs in ``/var/log/apache2/``.


What next?
----------

Some options for what to do next:

 - add more TwitterUsers and run user_timeline again
 - set up cronjobs for user_timeline and other daily operations
 - set up supervisord and use it to capture one or more streams
 - sign up to https://groups.google.com/forum/#!forum/sfm-dev to
   ask questions or suggest improvements
 - track SFM progress, file bug/enhancement tickets, fork the code
   and submit pull requests at:
   https://github.com/gwu-libraries/social-feed-manager
