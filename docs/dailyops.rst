.. Social Feed Manager Daily Operations file

Daily Operations
================

SFM is not a set-it-and-forget-it kind of application.  Things change
constantly on social media platforms like Twitter, so we have to check
constantly for these changes and act appropriately.  For example,
if you haven't yet read our summary of the :doc:`lifecycle of a
TwitterUser<\use_cases>`, read it now and come back, you'll see what
we mean.

We have added several commands and tweaks to the data model to account
for these changes as we've been running SFM for the past few years.
Please read through the descriptions below and consider how they should
apply in your scenario, as well as what might be missing that you will
want to supply yourself for your own environment, or perhaps to add to
SFM itself and submit back to the project.  There are likely to be more
of these to come as more people use the app, and we welcome your ideas.


Administrative tasks
--------------------

Once you have successfully :doc:`installed SFM<\install>` the first task
is to add app users; if at least one other person will be using the app,
go to the ``/admin/`` url and sign in with the administrative system account
you created during installation.  Under "Auth -> Users" you can add one or
more additional SFM users (ask them to set their password).  Once you've
saved a new user, you can edit them from the list of Users and give them
"superuser" status if you want them to be able to add users like you
can with your own admin account.  If one of these people ever leaves
your organization or stops using the app, you can set their account to
inactive by unchecking the "Active" box on their user edit page, too,
instead of deleting their account entirely.  Note that this functionality
is all provided out-of-the-box by Django itself, with no custom SFM code.

An alternate way to add a user is to let them sign in at the ``/`` url
by authenticating through Twitter.  The advantage of this approach is
that SFM will save a copy of authorized OAuth tokens for their account,
which you can use later to manage a stream-based filter for that user.
Once someone logs in successfully this way, you can edit their account
under ``/admin/`` just like any other SFM user, but note that you can end
up with two different SFM accounts for the same person by accident if
you use both methods.


Data gathering
--------------

Now that you and your colleagues have accounts for your SFM, you can
add TwitterUsers.  This is the simplest way to capture data using SFM.
From ``/admin/`` under "UI -> Twitter Users" add Twitter accounts to
capture by their names, one by one, by entering their account name in the
"Name" box.  Be careful to spell it correctly!  SFM will look up that
account by name and verify that it's a public account, and will then
store the Twitter UID.  Try adding a few accounts.

Now that there are a few TwitterUsers in your database, to capture
their recent tweets, use the :ref:`user_timeline` management command.
Run the command once, and you'll see updates of the data-fetching process
on the commandline.  As it proceeds, you can go to ``/`` in your app
and you'll see the data start to appear in the UI.  You can also go
to ``/admin/`` and see these same tweets in the admin UI under "UI ->
Twitter user items".  Finally, there will be a separate record of the
``user_timeline`` "job" you ran under "UI -> Twitter user timeline jobs".

As you capture tweets this way, you might want to create a record of
the urls linked to by shortened urls in tweet text.  To do this, use
the :ref:`fetch_urls` command.

Note that as you add more and more TwitterUsers and their tweet data,
both of these commands can take a long time -- even many hours -- to run.
It takes a while because SFM abides by the rate limits defined by the
Twitter API, leaving a little multi-second buffer between every call to
the API so the app never goes over the limits.  The more users you're
collecting, the longer it will take.

Both the ``user_timeline`` and ``fetch_urls`` commands are well suited
to being automated with something like a cronjob.  There are subtle
issues to consider here, though, namely that whenever you fetch a user's
tweets, the metadata associated with each tweet will be accurate as
of the moment you fetch it, rather than from the moment the tweet was
originally published.  This means that the first time you grab, say,
500 old tweets from a TwitterUser you just added, *every* one of those
500 tweets will contain exactly the same follower/following counts on
the TwitterUser.  Also, if that 500th tweet you capture is only five
minutes old, then the retweet count on your capture of that tweet only
accounts for the five minutes of that tweet's existence.  Older tweets
may have correspondingly higher retweet numbers.

It's important to understand these issues because how regularly you
capture tweets using ``user_timeline`` will determine how accurate these
numbers are.  If it is important to you to see how following/follower
counts change tweet by tweet, you'll want to run ``user_timeline`` often.
If it's important to get an accurate retweet count on each tweet, you
might want to run it less often.  Either way, there will be a bit of
a sliding time gap over the range of tweets you capture at any given
time because of these implementation details of the Twitter API, and
the relative accuracy for a given purpose of the metadata you capture
when you've captured it will vary accordingly.  It also means that
when you first capture a TwitterUser's older tweets you will not be
able to see how old tweets affected their follower/following counts.
These details might be important to users of the data you collect,
so please familiarize yourself with them.

At GW Libraries, as of July 2014, we track about 1,800 TwitterUsers,
running the ``user_timeline`` command on a cronjob every six hours.
We run the ``fetch_urls`` command on a cronjob once a day, limiting (with
the optional start and end date parameters) to the previous day's tweets.
Each of these jobs takes several hours to complete.  Our PostgreSQL
database for SFM uses over 6Gb in production, and a complete export of
the database to a single file compresses to about 1.5Gb.


Account maintenance
-------------------

Due to the many changes that can occur on a single TwitterUser account
(as described in :doc:`lifecycle of a TwitterUser</use_cases>`), you
should run :ref:`update_usernames` regularly as well.  Because SFM uses
the Twitter uid of a TwitterUser rather than the name to capture new data,
``user_timeline`` will continue to work if SFM doesn't have an updated
username even after the Twitter account name changes, but it's best all
around if you have a record of the changes over time, and if you're never
too far out of date.  At GW Libraries we've found that running it once
a week during the weekend suffices.

If the ``user_timeline`` or ``update_usernames`` scripts report
errors, such as an account no longer being available, or no longer
being public, you can deactivate a TwitterUser the ``/admin/`` UI under
"UI -> TwitterUsers", just search for that account by its name or uid,
click on its SFM id when you find it, then uncheck the "Is active"
box on the TwitterUser edit page.  When a TwitterUser is inactive,
``user_timeline`` will no longer check for new tweets, saving time and
rate limit capacity.  You can always re-activate a TwitterUser later if
its account changes again.


Data movage
-----------

If you are using one or more :doc:`Supervisord-managed
streams</supervisor_and_streams>` to capture filtered queries live off
the Twitter hose or the sample stream, you will want to establish an
appropriate set of scripts to handle the resulting files.  SFM has no
opinion about how you manage digital content, aside from a bias toward
gzipping text files at regular intervals. :)  You might want to set
up a cronjob pipeline to package up files using BagIt, or move them to
another server, or whatever works for you, but keep in mind that these
files can grow to fill up gigabytes and terabytes of storage quickly.

SFM does provide the :ref:`organizedata` management command to
walk through a set of gzipped stream files and sort them into a
year/month/date/hour-based folder structure.  This is optional, but
we find it convenient to spread files out on a filesystem, and for
the scripts we're working with to post-process files we generate at
appropriate time intervals.


System considerations
---------------------

These are outside of the scope of SFM proper, but worth keeping in mind.

It is best to establish a regular snapshot backup of the PostgreSQL SFM
database, and to rotate those files to a secondary storage environment.
This can help both with testing new versions of the software and should
you ever otherwise need to restore your database from scratch.

The same logic holds for taking a snapshot backup of your configuration
files, such as your ``local_settings.py`` and apache config file.  These
should be relatively easily reproduceable - you can get your OAuth keys
back from Twitter, for example - but it can be a pain to have to do so.

At GW Libraries we have a twice-daily cronjob that performs these
operations.
