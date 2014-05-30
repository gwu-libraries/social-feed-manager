.. Social Feed Manager Troubleshooting file

Troubleshooting
===============

TwitterUserItemUrls is empty.  Why isn't SFM fetching URLS?
-----------------------------------------------------------

Have you set up a cron job to run fetch_urls?


I tried to add a filterstream using the user that I've configured as TWITTER_DEFAULT_USER, but SFM is telling me that Streamsample is also configured to authenticate as that user.  But I'm not using Streamsample!
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

SFM makes the assumption that streamsample either is being used or may be
used in the future, and streamsample authenticates with the Twitter API using
TWITTER_DEFAULT_USER.  Due to Twitter API's rate limiting, SFM prevents
the possibility of having multiple streams (in this case, streamsample and a
filterstream) simultaneously calling the Twitter streaming API with the same Twitter user name.
