
m5_003 release notes
====================
     
**m5_003** is release which provides:

* Improvements to the extracts:

  * A header row with column titles has been added to the CSV version
  * A column has been added for ['coordinates'] when present in a tweet

* Efficiency improvements

  * Improvements to fetch_urls, making use of django-queryset-iterator and newer features of the requests library (thanks `@cazzerson <http://github.com/cazzerson/>`_)
  * UID lookups by name are now done using a single bulk lookup API call
  * tweet rehydration (with the ``fetch_tweets_by_id`` management command) is now done using a bulk API call (thanks `@edsu <http://github.com/edsu/>`_)

* Updated python dependencies, with tweepy version now pinned to 3.2.0 (prior to this, it was not pinned, and the app only worked with =< 2.3.0).  Requests is now constrained to > 2.4.1 
* Simplified naming scheme for the timestamped filterstream and samplestream files; colons have been removed from the naming scheme.
* Cleaner error messages in add_userlist.  add_userlist now provides more readable and specific messages when an account name was found to be invalid or suspended.
* Elimination of blank lines between tweets written to zip files by ``filterstream`` (thanks `@edsu <http://github.com/edsu/>`_).  **NOTE: This may affect any scripts that read or process your filterstream output files.**
* Better use of the Twitter streaming API through SFM TwitterFilters.  Rewrote TwitterFilter parsing of Words, People, and Location fields. These parameters now leverage the full capability of Twitter's streaming API, as follows:

  * *Words* (passed to Twitter ``track`` parameter).  Commas between terms function as logical ORs; spaces between terms function as logical ANDs. More information at `Twitter's documentation of the streaming request parameters <twitter_track_>`_.
  * *People* (passed to the Twitter ``follow`` parameter).  This parameter is now a comma-separated list of valid Twitter usernames.  Twitterfilters already present in SFM will be migrated as part of the database migration required for m5_003.  Prior to m5_003, People values had been sent (incorrectly) as account names rather than uids; they are now sent as uids.  Since the People parameter had been a space-separated list, People values are migrated to comma-separated lists.  The migration script also looks up and stores the Twitter id for each account in the People list; accounts whose ids were not found (e.g. suspended accounts, accounts not found, etc.) are logged in the migration log file.  When updating or saving a Twitterfilter in m5_003, SFM checks the validity of each of the values in the People list and will not allow saving to proceed if it contains an account name whose id cannot be found.
  * *Locations* (passed to the Twitter ``locations`` parameter).  This parameter should be a comma-separated list of numeric values, which each value between -180 and 180.  Each set of 4 values defines a geographic bounding box (long, lat, long, lat); a list of 8, 12, etc. values would define multiple bounding boxes.  While this parameter has not changed, m5_003 provides improved validation.
  

**NOTE: The requirements.txt file has changed, so upgrading to m5_003 requires updating python library dependencies within your virtualenv.**  To update dependencies:
::
  % source ENV/bin/activate
  % pip install -r requirements.txt

**NOTE: Upgrading to m5_003 requires running a database migration.**  To run the migration:
::
  % ./manage.py migrate ui

The migration number is 0026.  If any active TwitterFilters contained People values for which Twitter uids were not available (for example, if the account was not found or was suspended), then a migration log file, ``0026_migration.log``, is generated, listing the account names for which uids were not available.


See the `complete list of changes for milestone m5_003 in github <m5_003_>`_.

.. _m5_003: https://github.com/gwu-libraries/social-feed-manager/issues?q=is%3Aissue+is%3Aclosed+milestone%3Am5_003 
.. _twitter_track: https://dev.twitter.com/streaming/overview/request-parameters#track 
