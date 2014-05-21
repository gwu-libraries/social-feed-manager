
m4_001 release notes
====================
     
*April 28, 2014*

**m4_001** introduces collecting expanded urls in tweets, supervisord to manage multiple process, and enhances organizedata to structure data files. It also fixes the bugs produced due to supervisord and cleans up the twitteruser status and filterstream issues.

**Enhancements**

Social-feed-manager has streamsample and filterstream management commands which is used to fetch random or filterted twitter feed. These management process are automated using supervisord. Supervisord manages the streamsample and filterstream process, starting it and stopping these processes when required.


Supervisord control:

- Streamsample and filterstream are managed by supervisord, SFM no longer requires manual run of these commands, if supervisord is set up, everything is handled by supervisord. This is done using the    post_save signal sent from the UI to initiate these processes.
  You can have a look at the Supervsiord to manage processes and the signals used at the ticket description on github `tkt# 135`_.

.. _tkt# 135: https://github.com/gwu-libraries/social-feed-manager/issues/135

- Twitter API doesnt allow to have streamsample and filterstream working together, hence a validation check on the admin UI while adding the filters using twitterfilter.
  validate active streams do not conflict `tkt# 133`_.

.. _tkt# 133: https://github.com/gwu-libraries/social-feed-manager/issues/133

- To maintain a proper nomenclature and avoid confusion and chaos, renamed rules in admin UI to twitterfilter and throughout SFM. 
  Rules renamed to twitterfilter `tkt# 170`_.

.. _tkt# 170: https://github.com/gwu-libraries/social-feed-manager/issues/170

Twitter data organization:

- The files handling the stream data can be organized  into levels of directory structure.Organizedata is a method to achieve that.
  organize data to use subdirs for different filters `tkt# 132`_.

.. _tkt# 132: https://github.com/gwu-libraries/social-feed-manager/issues/132

- A new table to store the urls if any present in the tweets of the accounts registered in SFM. The whole expanded form of url is stored in Twitteruseritemurl.
  expand urls `tkt# 119`_.

.. _tkt# 119: https://github.com/gwu-libraries/social-feed-manager/issues/119

**Issues and bugfixes**

- Issue: The signal sent from the twitterfilter adding UI, goes in and creates all the twitterfilter configuration files everytime a new twitterfilter is added. It should in general, go and create configuration file for only that specific twitterfilter.twitterfilter signal bug `tkt# 177`_.

.. _tkt# 177: https://github.com/gwu-libraries/social-feed-manager/issues/177

fix: Made the signal call to intiate the createconf process for respective filterid.
  twitterfilter signal changes `tkt# 179`_.

.. _tkt# 179: https://github.com/gwu-libraries/social-feed-manager/pull/179

- Issue: TwitterUser accounts which are no longer valid and hence needs to be updated with is_active=False in SFM, the Twitter API doesnt allow to do that, as the API doesnt return the status of a twitter account which is suspended or deleted. cannot update TwitterUser user status for no-longer-valid acct `tkt# 150`_.
        
.. _tkt# 150:   https://github.com/gwu-libraries/social-feed-manager/issues/150

fix:  Added logic to validate error and added clean() method.
      Added logic to throw clean ValidationErrors if name is not unique `tkt# 152`_.

.. _tkt# 152: https://github.com/gwu-libraries/social-feed-manager/pull/152
