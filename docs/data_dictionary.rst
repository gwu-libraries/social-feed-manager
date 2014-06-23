.. Social Feed Manager Data Dictionary

CSV Export Data Dictionary
==========================

While Social Feed Manager captures the entire JSON data for each tweet, the csv export for each user timeline outputs selected processed fields.

For more info about source tweet data, see Twitter API documentation, including `Tweets <https://dev.twitter.com/docs/platform-objects/tweets>`_ and `Entities <https://dev.twitter.com/docs/platform-objects/entities>`_.

+-------------------------+-----------------------------------------------------+--------------------------------------------------+ 
| Field	                  | Description                                         | Example                                          |
+=========================+=====================================================+==================================================+ 
| sfm_id                  | SFM internal identifier for tweet	                | 6114                                             |
|                         |                                                     |                                                  | 
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| created_at              | UTC time when the tweet was created	                | 2013-10-28T17:52:53Z                             | 
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| created_at_date         | date in Excel-friendly format, MM/DD/YYYY           | 10/28/2013                                       |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| twitter_id              | Twitter identifier for the tweet	                | 114749583439036416                               |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| screen_name             | The screen name, handle, or alias that this user    | NASA                                             |
|                         | identifies themselves with. Screen_names are unique |                                                  |
|                         | but subject to change.                              |                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| followers_count         | Number of followers this account had at the time    | 235                                              |
|                         | the tweet was harvested                             |                                                  | 
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| friends_count           | Number of users this account is following at the    | 114                                              |
|                         | time the tweet was harvested                        |                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| retweet_count           | Number of times the tweet has been retweeted at the | 25                                               | 
|                         | time the tweet was harvested. If the tweet is a     |                                                  | 
|                         | retweet AND the retweet was done using the Twitter  |                                                  | 
|                         | retweet feature (i.e. is_reweet_strict = TRUE) the  |                                                  |
|                         | retweet_count reflects the retweet count for the    |                                                  |
|                         | original tweet. If the retweet was done by typing RT|                                                  |
|                         | at the beginning (is_retweet_strict = FALSE) the    |                                                  |
|                         | retweet_count reflects retweets of the retweet.     |                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| hashtags                | Hashtags which have been parsed out of the tweet    | Mars, askNASA                                    |
|                         | text, separated by a comma and space                |                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| in_reply_to_screen_name | If the tweet is a reply, the screen name of         | wiredscience                                     |
|                         | the original tweet's author                         |                                                  | 
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| mentions                | Other Twitter users mentioned in the text of the    | @NASA_Airborne, @NASA_Ice                        | 
|                         | tweet, separated by comma and space.                |                                                  | 
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| twitter_url             | URL of the tweet. If the tweet is a retweet made    | http://twitter.com/NASA/status/394883921303056384|
|                         | using the Twitter retweet feature, the URL will     | retweet redirecting to original tweet:           | 
|                         | redirect to the original tweet                      | http://twitter.com/NASA/status/394875351894994944|
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| is_retweet_strict       | Tweet is a retweet of another tweet, using Twitter's| FALSE                                            | 
|                         | retweet function                                    |                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| is_retweet              | SFM's best guess at whether tweet is a retweet of   | TRUE                                             |
|                         | another tweet; includes retweets accomplished using |                                                  |
|                         | old-style method of placing RT in front of tweet    |                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| text                    | The UTF-8 text of the tweet                         | Observing Hurricane Raymond Lashing Western      | 
|                         |                                                     | Mexico: Low pressure System 96E developed quickly|
|                         |                                                     | over the... http://t.co/YpffdKVrgm               |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| url1                    | First URL in text of tweet, as shortened by Twitter | http://t.co/WGJ9VmoKME                           |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| url1_expanded           | Expanded version of URL; URL entered by user and    | http://instagram.com/p/gA_zQ5IaCz/               |
|                         | displayed in Twitter. May itself be a user-shortened|                                                  |
|                         | URL, e.g. from bit.ly. Further expansion available  |                                                  |
|                         | in sfm web interface, not in csv export.            |                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| url2                    | Second URL in text of tweet, as shortened by Twitter|                                                  |
|                         |                                                     |                                                  |
+-------------------------+-----------------------------------------------------+--------------------------------------------------+
| url2_expanded           | Expanded version of URL; URL entered by user and    |                                                  |
|                         | displayed in Twitter. May itself be a user-shortened|                                                  |
|                         | URL, e.g. from bit.ly. Further expansion available  |                                                  |
|                         | in SFM web interface, not in csv export             |                                                  |
|                         |                                                     |                                                  | 
+-------------------------+-----------------------------------------------------+--------------------------------------------------+ 




