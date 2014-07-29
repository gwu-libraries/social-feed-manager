
m4_002 release notes
====================
     
**m4_002** improves process management under Supervisord.  Previously
it was necessary to start and stop SFM's supervisord-managed processes
using the supervisorctl tool at the command line.

With m4_002, SFM now automatically starts and stops twitterfilter
processes when TwitterFilters  are created, activated, deactivated, or
deleted by an SFM admin user.

A new management command, :ref:`fetch_tweets_by_id`, was also added.  Given
a list of tweet ids, the command fetches the associated tweets as JSON.

**Significant issues and bugfixes**

- #89 - Added management command to fetch tweets by a list of tweet ids.

- #154 - Enabled supervisord to pick up new twitterfilter conf files and
  initiate processes correctly.
 
See the `complete list of changes for milestone m4_002 in github <m4_002_>`_.

.. _m4_002: https://github.com/gwu-libraries/social-feed-manager/issues?milestone=7&page=1&state=closed



