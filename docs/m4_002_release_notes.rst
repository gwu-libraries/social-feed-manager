
m4_001 release notes
====================
     
**m4_002** improves process management under Supervisord.


**Issues and bugfixes**

With m4_001 release, supervsiord can be used to manage the filterstream
and samplestream management commands. When the supervisord is set-up
for the first time it picks up the filterstream conf files to add as
the managed sub-process under it.

- #154 - Enabled supervisord to pick up new twitterfilter conf files and
  initiate processes correctly.
 
See the `complete list of changes for milestone m4_002 <m4_002_>`_.

.. _m4_002: https://github.com/gwu-libraries/social-feed-manager/issues?milestone=7&page=1&state=closed



