
m4_001 release notes
====================


**m4_001** introduces collecting expanded urls in tweets, improves use
of supervisord to manage multiple processes, and enhances organizedata
to better structure data files. It also fixes bugs related to supervisord
and cleans up twitteruser status and filterstream issues.

If you are upgrading an existing SFM instance from a version prior to
m4_001, to m4_001 or newer, and your instance contains active TwitterFilters,
then you will need to run the :ref:`createconf` management command.

**Enhancements**

Social Feed Manager has streamsample and filterstream management
commands which are used to fetch random or filtered twitter feeds. These
management process are automated using supervisord. Supervisord manages
the streamsample and filterstream processes, starting and stopping
these processes when required.


Supervisord control:

- #135 - streamsample and filterstream are managed by supervisord, SFM no
  longer requires manual run of these commands, if supervisord is set up,
  everything is handled by supervisord. This is done using the post_save
  signal sent from the UI to initiate these processes.


- #133 - Twitter API doesn't allow parallel streams like streamsample and
  filterstream to run concurrently with the same authorization
  credentials, so run a validation in the admin UI when adding the filters
  using twitterfilter, and validate that active streams do not conflict.

- #170 - To simplify naming, renamed rules in admin UI to twitterfilter
  and throughout SFM.


Twitter data organization:

- #132 - Re-fit organizedata to use subdirs for different filters.


- #119 - Added command and table to fetch and store expanded form of urls 
  found in tweets.


**Other issues and bugfixes**

- #177 - Refactored signal call to createconf to be specific to the appropriate
  filter.

- #150 - Better handling of deactivation of TwitterUser status for no-longer 
  Twitter-valid accounts, validating and throwing errors if name is not unique.


See the `complete list of changes for milestone m4_001 in github <m4_001_>`_.

.. _m4_001: https://github.com/gwu-libraries/social-feed-manager/issues?milestone=5&state=closed

