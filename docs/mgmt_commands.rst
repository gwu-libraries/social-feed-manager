
Management Commands
====================

Introduction
------------

Many of the key back-end functions of Social Feed Manager (SFM) are invoked
using management commands.  The SFM management commands are standard `Django
management commands <https://docs.djangoproject.com/en/1.6/ref/django-admin/>`_.  As such, they are invoked like any other Django
management commands:

1. First make sure that your virtualenv is activated.

.. code-block:: none

   $ source ENV/bin/activate

2. From ``<PROJECT_ROOT>/sfm``, execute ``./manage.py`` followed by the
   desired management command, arguments and options.

.. code-block:: none

   $ cd sfm
   $ ./manage.py <command> [args] [options]

SFM management commands may be run:

* manually (i.e. at the command line),
* using cron jobs, and/or
* using supervisord (in the case of filterstream and streamsample)
  as described in **TODO: Link to other section**

Each SFM management command is described below.


user_timeline
-------------

**user_timeline** calls the Twitter API to retrieve the available tweets for
either all *active* TwitterUsers in SFM, or for a specific *active* 
TwitterUser.  Each tweet is created as a TwitterItem in SFM.

user_timeline connects to the Twitter API as ``TWITTER_DEFAULT_USERNAME``, and
requests the user_timeline by the Twitter account uid (not by account name).
Through the tweepy library, it calls the `Twitter API user_timeline method <https://dev.twitter.com/docs/api/1/get/statuses/user_timeline>`_.

For each TwitterUser user_timeline requests only tweets since the newest
tweet that was previously retrieved.  If no tweets were previously retrieved
for that TwitterUser, it requests as many tweets as the Twitter API will
provide (up to the 3200 most recent tweets).

To fetch tweets for all active TwitterUsers in SFM:

.. code-block:: none

   ./manage.py user_timeline

To fetch tweets for a specific twitter user:

.. code-block:: none

   ./manage.py user_timeline --user='twitter username'

The full specification of user_timeline options can be viewed using --help:

.. code-block:: none

   ./manage user_timeline --help

Sample output for user_timeline:

.. code-block:: none
    
    user: pinkfloyd
    since: 1
    saved: 200 item(s)
    since: 1
    max: 326988934884249599
    saved: 200 item(s)
    since: 1
    max: 168992796676591616
    saved: 199 item(s)
    since: 1
    max: 117550550098247679
    saved: 86 item(s)
    stop: < 150 new statuses

update_usernames
----------------

Twitter account owners can, and often do, change the names of their accounts,
although an account's UID never changes.

update_usernames looks up the names of the Twitter accounts corresponding to
all active TwitterUsers.  If a Twitter account's name has changed since SFM
last verified the account's name, update_usernames will update the name of the
TwitterUser, and will append the former name (and timestamp) to the TwitterUser's former_names value.  former_names is a json field; an example would be:

``{"2014-02-19T21:50:56Z": "OldName", "2014-01-16T13:49:02Z": "EvenOlderName"}``

Note that update_username is case sensitive; a change in capitalization *is*
considered a name change.

To update names of all active TwitterUsers:

.. code-block:: none

   ./manage.py update_usernames

To update names of a specific active TwitterUser, by its current name in SFM:

.. code-block:: none

   ./manage.py update_usernames --user='current TwitterUser name in SFM'


populate_uids
--------------

.. deprecated:: m5_001


streamsample
------------

The Twitter API provides a streaming interface which returns a random sample (approximately 0.5%)
of all public tweets.  The SFM streamsample management command directs the content of this stream
to files.  The location of these output files is determined by the DATA_DIR variable in the
local_settings.py configuration file.  As streamsample is intended to be run as an ongoing,
streaming process, SFM provides a streamsample.conf.template file in
<PROJECT ROOT>/sfm/sfm/supervisor.d that can be copied to streamsample.conf and edited to
include the relevant pathnames, so that it can be run and managed using supervisord.

Streamsample currently generates around 1 GB worth of tweet data per day, so it is important to
plan storage capacity accordingly.

To run manually and view streaming output to the console:

.. code-block:: none

     ./manage.py streamsample

To run manually and direct output to files in DATA_DIR:

.. code-block:: none

     ./manage.py streamsample –save

Information on the Twitter API streamsample resource:
https://dev.twitter.com/docs/api/1.1/get/statuses/sample


filterstream
------------

The Twitter API provides a streaming interface which returns tweets that match one or more filter
predicates.  SFM administrative users can create multiple TwitterFilters, each with its own
predicate parameters.  The SFM filterstream management command directs the content of 
one or more active TwitterFilters to files.  The location of these output files is determined by
the DATA_DIR variable in the local_settings.py configuration file. 

Filterstream is intended to be run as a set of ongoing, streaming processes; SFM automatically
generates the necessary supervisord configuration files.  However, generation of these files
requires the DATA_DIR, SUPERVISOR_PROCESS_USER, and SUPERVISOR_UNIX_SOCKET_FILE settings
variables to be configured in local_settings.py .

Each TwitterFilter may contain the following predicates:

Words - Keywords to track

People - Twitter accounts to track

Location - Geographic bonuding boxes to track

To run manually and view streaming output to the console:

.. code-block:: none

     ./manage.py filterstream

To run manually and direct output to files in DATA_DIR:

.. code-block:: none

     ./manage.py filterstream –save

Filterstream can also take a parameter corresponding to the number of an individidual
TwitterFilter, e.g.

.. code-block:: none

     ./manage.py filterstream 4 –save

This will run only TwitterFilter with an id of 4.  If no TwitterFilter number is given,
filterstream will run for all active TwitterFilters.

Information on the Twitter API filter streaming resource:
https://stream.twitter.com/1.1/statuses/filter.json


organizedata
------------
The filterstream and streamsample produces gigs of data in numerous file.Organizedata is a feature in SFM which enhances the directory structure for storing these files.The nomenclature of the output files contains the date and day timestamp for each file.This timestamp is then utilized to form a directory structure such that, each file is organized in directories per their type, year, month and then date.

To run:

Organize the tons of files in sub-directories:
    ./manage.py organizedata

fetch_urls
----------
Fetch_urls is a feature in SFM, which allows you to store the urls in every tweet explicitly.You can view the expanded urls at admin page, under the twitteruseritemurl.
Fetch_urls also provides you with options to mention as the criteria to fetch these urls. The options available are:

1.Startdate -- The earliest date from where you want to fetch the urls

2.Enddate -- The latest date, untill which you want to fetch the urls

3.twitteruser -- The specific twitter username you want to fetch the url for

4.limit -- the limit in integers as to how many urls you will like to fetch

5.refetch -- refetch the fetched urls.

To run:
    ./manage.py fetch_urls 

export_csv
----------
SFM allows you to save the tweets from every twitter username, in the form of csv reports.A detailed explanation of the report can be found at the Data Dictionary at the about page in SFM UI http://gwsfm-prod.wrlc.org/about/   
The report can be downloaded from the SFM UI directly, otherwise you can use the command as mentioned below to extract reports.The various options which can be given as the criteria to extract the report are:

1.start-date -- returns the tweets starting from the specified date.

2.end-date -- returns the tweets ending at the specified date.

3.twitter-user -- returns all the tweets for the specified date

4.set-name -- allows you ro customise the file name of the csv report.

To run:

extract the CSV report
       ./manage.py export_csv

createconf
----------
Createconf command is used to create the configuration files.These conf files are the sub-processes picked up by Supervisord.By default, Supervisord is configuired to initiate the streamsample subprocess, while the filtrestream conf files are dynamically added as sub-process under supervisord. This command is signaled to execute when a twitter filter is added to the system. 

To run manually:

    ./manage.py createconf --twitter-filter

Read more about the superviord conf:
LINK 
