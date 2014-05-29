
m4_001 release notes
====================
     
**m4_002** has changes to manage the process under Supervisord.


**Issues and bugfixes**

With m4_001 release, supervsiord can be used to manage the filterstream and samplestream management commands. When the supervisord is set-up for the first time it picks up the filterstream conf files to add as the managed sub-process under it.

- Issue -If supervisord is already running, and new filters are added with filterstream, the supervsiord fails to pick up the newly added conf files, and hence the new twitter-filter doesnt start.

Fix- The fix includes a change which enables supervisord to pick up the new twitter-filter conf files and initiate their process.tkt#154

The link of changes for release `m4_002`_.

.. _m4_002: https://github.com/gwu-libraries/social-feed-manager/issues?milestone=7&page=1&state=open



