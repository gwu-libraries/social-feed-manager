
m5_001 release notes
====================
     
**m5_001** is the documentation release.SFM now has an elaborate documentation on what it does, how it does and what it can do. 


**Documentation**
contains a list of docs explaining :

-Getting started

-the installation and working of social-feed-manager. 

-its current use-cases, where and how its used now, and its scopes of enhancements.

-user-life cycle

-features, how you can use them and automate them

-FAQs and troubleshooting

For more details visit `Social-Feed-Manager docs`_.

.. _Social-Feed-Manager docs: http://social-feed-manager.readthedocs.org/

**Issues and Bugfixes**

* Issue: The addition of TwitterUser in SFM also allowed to update its name afte the User is added, hence sometimes allowing to add new/changed username to same SFM ID, hence storing data for two different twitteruser accounts under same sfm id.

Fix: Added a change so the twitterusername can be validated and name edits prevented.

The list of tickets for `m5_001 milestone`_.

.. _m5_001 milestone: https://github.com/gwu-libraries/social-feed-manager/issues?milestone=6&page=1&state=open
