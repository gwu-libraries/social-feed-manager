
m5_002 release notes
====================
     
**m5_002** is release which provides:

* a new management command, add_userlist, to add a list of users in bulk.
  This command can also add the new users to a TwitterUserSet
* a new /status page available to admin users.  This page displays the
  current status of all supervisord-managed SFM streams
* a new --list option for the filterstream management command, to display
  the current status of all supervisord-managed SFM streams
* improvements to the CSV export 
* links available in the UI header are now consistent across different pages
* an Excel (.xls) download link available on user timeline pages
* a new management command to export user timelines in .xls format
* encoding improvements in the CSV export
* improved instructions for supervisord setup and configuration
* minor documentation fixes

See the `complete list of changes for milestone m5_002 in github <m5_002_>`_.

.. _m5_002: https://github.com/gwu-libraries/social-feed-manager/issues?q=milestone%3Am5_002+is%3Aclosed
