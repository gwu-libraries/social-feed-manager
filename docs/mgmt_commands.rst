Management Commands
====================

Social-feed-manager(SFM) has  features which allows you to store the tweets from users, download those tweets,  stream public statues, update their usernames, fetch urls in tweets, filter and capture public statues, collect random samples of twitter data and many more. These features are present as management command under SFM, their description and usage is mentioned below.

user_timeline
-------------
Twitter API allows you to fetch the user timeline for a particular username.SFM uses this API to fetch and then store the tweets of a particular twitter user or a list of twitter users.For the new twitter users added, it goes in a fetches approximately the last 3200 tweets, then gradually fetches latest tweets.It is automated to run every two hours to collect tweets. You can run this command manually as well, as mentioned below:

To run:

Fetch tweets for all the twitter users present in SFM 
       ``./manage.py user_timeline``

Fetch tweets for the specific twitter user
       ``./manage.py user_timeline - -user = 'twitter username'``

Check more options for user_timeline, use 
       ``./manage.py user_timeline - -help``

Sample output for User_timeline:


.. code-block:: none
    
    user: pinkfloyd
    since: 1
    saved: 200 item(s)
    since: 1
    max: 326988934884249599
    saved: 200 item(s)
    since: 1
    max: 168992796676591616
    saved: 199 item(s)
    since: 1
    max: 117550550098247679
    saved: 86 item(s)
    stop: < 150 new statuses

For more information visit `Twitter API`_.

.. _Twitter API:  https://dev.twitter.com/docs/api/1/get/statuses/user_timeline

update_usernames
----------------
Twitter allows account holders to update their user-name. update_username feature enables SFM to update the user-names of twitter users if any user-names have been changed. It is automated to run once everyday to verify and update any twitter users with new updated user-names. You can run it manually as well, as mentioned below:

To run :

Verifies and Updates any user-name changed for any twitter users 
       ``./manage.py update_usernames``

Verify and Update user-name for a specific twitter user 
       ``./manage.py update_usernames - -user='twitter user-names'``

       (Need to add the output)

populate_uids
--------------
Populate_uid is now a depricated command, as it is now executed implicitly.
Twitter accounts have a unique uid associated with it. Each twitter user stored in SFM, is populated with its unique uid as well. This command fetches these uids using the twitter user-names.It is automated, and is signaled to execute whenever a new twitter user is added in the system.

streamsample
------------
Twitter Api allows to stream samples of public statuses. SFM uses this API,to fetch streams of these random samples and stores them in files. The location of these output files is configured by the authenticated user at the time of the installation. Streamsample runs constanly, especially when configured with supervisord, hence fetching gigs of data in the files.

To run:

Fetch and save to file samples       
       ``./manage.py streamsample - -save``

View samples on console
       ``./manage.py streamsample``

Automated sample fetch
      You need to follow the supervisord installation and configuration settings. (LINK)

Sample output streamsample:

.. code-block:: none

    {"delete":{"status":{"id":465921613243113473,"user_id":143312522,"id_str":"465921613243113473","user_id_str":"143312522"}}}^M
     
     {"created_at":"Mon May 12 18:45:52 +0000 2014","id":465925845312606210,"id_str":"465925845312606210","text":"next weekend is #pride long beach! Finally, cant wait!!!","source":"\u003ca href=\"http:\/\/    twitter.com\/download\/android\" rel=\"nofollow\"\u003eTwitter for Android\u003c\/a\u003e","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,
     "in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":2213376380,"id_str":"2213376380","name":"Mona Lefleur","screen_name":"MonaLefleur","location":"Hollywood, California","url":null, "description":"IG @monalefleur","protected":false,"followers_count":62,"friends_count":109,"listed_count":1,"created_at":"Mon Nov 25 02:15:29 +0000 2013","favourites_count":993,"utc_offset":null,
     "time_zone":null,"geo_enabled":true,"verified":false,"statuses_count":2554,"lang":"en","contributors_enabled":false,"is_translator":false,"is_translation_enabled":false,"profile_background_color":         "C0DEED","profile_background_image_url":"http:\/\/pbs.twimg.com\/profile_background_images\/378800000123287236\/fbc8528ea15708a07515a1428d8d350d.jpeg","profile_background_image_url_https":"https:\/\/pbs.
     twimg.com\/profile_background_images\/378800000123287236\/fbc8528ea15708a07515a1428d8d350d.jpeg","profile_background_tile":true,"profile_image_url":"http:\/\/pbs.twimg.com\/profile_images\/                465724842738593792\/XVBrhbMf_normal.jpeg","profile_image_url_https":"https:\/\/pbs.twimg.com\/profile_images\/465724842738593792\/XVBrhbMf_normal.jpeg","profile_banner_url":"https:\/\/pbs.twimg.com\/
     profile_banners\/2213376380\/1385347154","profile_link_color":"0084B4","profile_sidebar_border_color":"000000","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333",                          "profile_use_background_image":true,"default_profile":false,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,
     "contributors":null,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[{"text":"pride","indices":[16,22]}],"symbols":[],"urls":[],"user_mentions":[]},"favorited":false,"retweeted":false,         "filter_level":"medium","lang":"en"}^M


For more information visit `Twitter samplestream API`_.

.. _Twitter samplestream API:  https://dev.twitter.com/docs/api/1.1/get/statuses/sample


filterstream
------------
Twitter API allows to fetch public statues using one or more filter predicates. SFM uses this API to fetch a series of public statues per the parameters mentioned in the filters. The output genertaed by filterstream is stored in files, the path for the output files is mentioned at the time of the installation.The three categories, which can be passed as the parameters for filtering the tweets are :

Words - Returns public statues containing the words mentioned in this parameter.    

People - Returns public stream on the basis of usernames mentioned in this parameter.

Location- Returns public stream in a particular geographic location mentioned in this parameter.
          This parameter is not upgraded as yet, hence should not be used.

To run:
Fetch and save to file       
       ``./manage.py filterstream - -save``

View samples on console
       ``./manage.py filterstream``

Automated filter sample fetch
      You need to follow the `supervisord`_ installation and configuration settings. 

.. _supervisord: http://social-feed-manager.readthedocs.org/supervisor_and_streams.html


For more information visit `Twitter filterstream API`_.

.. _Twitter filterstream API:  https://stream.twitter.com/1.1/statuses/filter.json

.. code-block:: none

    {"created_at":"Fri May 09 20:15:40 +0000 2014","id":464861280613187584,"id_str":"464861280613187584","text":"http:\/\/t.co\/PptT8rWgm2   \u041c\u0438\u0441\u0442\u0440\u0430                                \u043e\u0431\u0434\u0443\u043c\u0430\u043b\u0430 \u0441\u0432\u043e\u0438 \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u0438. \u0415\u0441\u043b\u0438
    \u0411\u044d\u0439\u043d              \u0431\u0443\u0434\u0435\u0442  \u043d\u0430\u0441\u0442\u043e\u043b\u044c\u043a\u043e  \u0433\u043b\u0443\u043f,  \u0447\u0442\u043e","source":"web","truncated":false,"in_reply_to_status_id":null,        "in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":1438364906,"id_str":"1438364906","name":"\u0412\u0430\u0441\u044f
    \u0411\u0430\u043d\u0434\u0438\u0442","screen_name":"BanditVasya","location":"\u0420\u044f\u0437\u0430\u043d\u044c","url":null,"description":"\u041d\u0435 \u0443\u043c\u0435\u0435\u0448\u044c              \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c \u0445\u043e\u0440\u043e\u0448\u043e - \u0440\u0430\u0431\u043e\u0442\u0430\u0439 \u043c\u043d\u043e\u0433\u043e!","protected":false,"followers_count":231,
    "friends_count":253,"listed_count":0,"created_at":"Sat May 18 13:11:28 +0000 2013","favourites_count":0,"utc_offset":null,"time_zone":null,"geo_enabled":false,"verified":false,"statuses_count":178,"lang": "ru","contributors_enabled":false,"is_translator":false,"is_translation_enabled":false,"profile_background_color":"BADFCD","profile_background_image_url":"http:\/\/abs.twimg.com\/images\/themes\/theme12\/
    bg.gif","profile_background_image_url_https":"https:\/\/abs.twimg.com\/images\/themes\/theme12\/bg.gif","profile_background_tile":false,"profile_image_url":"http:\/\/pbs.twimg.com\/profile_images\/        3676268819\/78932aa21de122b8de65423436626be8_normal.jpeg","profile_image_url_https":"https:\/\/pbs.twimg.com\/profile_images\/3676268819\/78932aa21de122b8de65423436626be8_normal.jpeg",
    "profile_banner_url":"https:\/\/pbs.twimg.com\/profile_banners\/1438364906\/1368882784","profile_link_color":"FF0000","profile_sidebar_border_color":"F2E195","profile_sidebar_fill_color":"FFF7CC",         "profile_text_color":"0C3E53","profile_use_background_image":true,"default_profile":false,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,
    "coordinates":null,"place":null,"contributors":null,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[],"symbols":[],"urls":[{"url":"http:\/\/t.co\/PptT8rWgm2","expanded_url":"http:\/\/         kinoprostotraf.ru\/noj-42\/","display_url":"kinoprostotraf.ru\/noj-42\/","indices":[0,22]}],"user_mentions":[]},"favorited":false,"retweeted":false,"possibly_sensitive":false,"filter_level":"medium",      "lang":"ru"}^M

organizedata
------------
The filterstream and streamsample produces gigs of data in numerous file.Organizedata is a feature in SFM which enhances the directory structure for storing these files.The nomenclature of the output files contains the date and day timestamp for each file.This timestamp is then utilized to form a directory structure such that, each file is organized in directories per their type, year, month and then date.

To run:

Organize the tons of files in sub-directories:
       ``./manage.py organizedata``

fetch_urls
----------
Fetch_urls is a feature in SFM, which allows you to store the urls in every tweet explicitly.You can view the expanded urls at admin page, under the twitteruseritemurl.
It also provides you with options to mention as the criteria to fetch these urls. The options available are:

* Startdate -- The earliest date from where you want to fetch the urls

* Enddate -- The latest date, untill which you want to fetch the urls

* twitteruser -- The specific twitter username you want to fetch the url for

* limit -- the limit in integers as to how many urls you will like to fetch

* refetch -- refetch the fetched urls.

To run:

      ``./manage.py fetch_urls``

export_csv
----------
SFM allows you to save the tweets from every twitter username, in the form of csv reports.A detailed explanation of the report can be found at the Data Dictionary at `about page`
.. _about page: http://gwsfm-prod.wrlc.org/about/   
The report can be downloaded from the SFM UI directly, otherwise you can use the command as mentioned below to extract reports.The various options which can be given as the criteria to extract the report are:

Options--

* start-date -- returns the tweets starting from the specified date.

* end-date -- returns the tweets ending at the specified date.

* twitter-user -- returns all the tweets for the specified date

* set-name -- allows you ro customise the file name of the csv report.

To run:

extract the CSV report
       ``./manage.py export_csv - -[options]``
    
createconf
----------
Createconf command is used to create the configuration files.These conf files are the sub-processes picked up by Supervisord.By default, Supervisord is configuired to initiate the streamsample subprocess, while the filtrestream conf files are dynamically added as sub-process under supervisord. This command is signaled to execute when a twitter filter is added to the system. 

To run manually:

      ``./manage.py createconf - -twitter-filter``

Read more about the `supervisord conf`_.

.. _`supervisord conf`:  http://social-feed-manager.readthedocs.org/supervisor_and_streams.html#Filterstream-setup
