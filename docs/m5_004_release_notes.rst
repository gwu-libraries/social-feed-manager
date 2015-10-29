
m5_004 release notes
====================
     
**m5_004** is release which provides:

* Docker support (see https://github.com/gwu-libraries/social-feed-manager/blob/m5_004/docker/README.md)
* Extract files now in XLSX format (was XLS).  The XLSX format removes the limitation
  of 65,536 rows.  SFM m5_004 substituted the openpyxl library for xlwt.
* SFM now uses tweepy v3.4.0.  This seems to eliminate the problem observed in m5_003,
  which used tweepy 3.2.0, where filterstream jobs stopped writing and/or slowed down
  the server.
* Several documentation improvements, mostly around installation and around supervisor/filterstreams setup.
* UI cleanup:  Improved consistency of date-time format rendering.
* Enhanced validation logic around checking People values when adding or updating filterstreams:
  If one or more People account names wasn't found when checking against Twitter, the TwitterFilter
  does save, but presents a warning listing the invalid accounts.
* Now allows deletion of filterstreams even if Supervisor isn't running.
* Now allows creation/update of filterstreams even if Supervisor isn't running (however, these won't automatically reflect updates when Supervisor is restarted (See `#376 <https://github.com/gwu-libraries/social-feed-manager/issues/376>`_).
* Updated Apache2 configuration file to note recommended changes for deployment on Ubuntu 14 / Apache2 v2.4+
* Enhanced fetch_urls to more gracefully handle (skip) truncated URLs that may appear in retweets with an ellipsis, and to pull URLs from 'media' if possible.
* And several other minor enhancements.

See the `complete list of changes for milestone m5_004 in github <m5_004_>`_ as well as the `code changes from m5_003 to m5_004 <m5_003_to_m5_004_diff_>`_.

Upgrade Notes:

* The requirements.txt file has changed, so Python library dependencies must
  be updated within your virtualenv.  To update dependencies:

::

  % source ENV/bin/activate
  % pip install -r requirements.txt


Contributors:

* Dan Chudnov, Dan Kerchner, Laura Wrubel, Justin Littman, Ankushi Sharma, and Rajat Vij at The George Washington University Libraries
* Ed Summers at Maryland Institute for the Humanities (MITH)
* Martin Klein at UCLA Research Library


.. _m5_004: https://github.com/gwu-libraries/social-feed-manager/issues?q=is%3Aissue+is%3Aclosed+milestone%3Am5_004 
.. _twitter_track: https://dev.twitter.com/streaming/overview/request-parameters#track 
.. _m5_003_to_m5_004_diff: https://github.com/gwu-libraries/social-feed-manager/compare/m5_003...m5_004
