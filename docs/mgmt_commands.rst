
Management Commands
====================

Social-feed-manager(SFM) has a features which allows you to store the tweets from users, stream public statues, update their usernames et al. These features are present as management command under SFM, their description and usage is mentioned below:

user_timeline
-------------
Twitter API allows you to fetch the user timeline for a particular username.SFM uses this API to fetch and then store the tweets of a particular twitter user or a list of twitter users. It is automated to run every two hours to collect tweets. You can run this command manually as well, as mentioned below:

To run:     

Fetch tweets for all the twitter users present in SFM 
     ./manage.py user_timeline

Fetch tweets for the specific twitter user
     ./manage.py user_timeline - -user = 'twitter username'

Check more options for user_timeline, use 
     ./manage user_timeline - -help

Detailed API explanation :
https://dev.twitter.com/docs/api/1/get/statuses/user_timeline

update_usernames
----------------
Twitter allows account holders to update their user-name. update_username feature enables SFM to update the user-names of twitter users if any user-names have been changed. It is automated to run once everyday to verify and update any twitter users with new updated user-names. You can run it manually as well, as mentioned below:

To run :

Verifies and Updates any user-name changed for any twitter users 
     ./manage.py update_usernames

Verify and Update user-name for a specific twitter user 
    ./manage.py update_usernames –user='twitter user-names

populate_uids
--------------
Twitter accounts have a unique uid associated with it. Each twitter user stored in SFM, is populated with its unique uid as well. This command fetches these uids using the twitter user-names.It is automated, and is signaled to execute whenever a new twitter user is added in the system. This command is now deprecated.

streamsample
------------
Twitter Api allows to stream samples of public statuses. SFM uses this API,to fetch streams of these random samples and stores them in files. The location of these output files is configured by the authenticated user at the time of the installation. Streamsample runs constanly, especially when configured with supervisord, hence fetching gigs of data in the files.

To run:

Fetch and save to file samples       
     ./manage.py streamsample –save

View samples on console
     ./manage.py streamsample

Automated sample fetch
      You need to follow the supervisord installation and configuration settings. (LINK)

Detailed API explanation: 
https://dev.twitter.com/docs/api/1.1/get/statuses/sample

filterstream
------------
Twitter API allows to fetch public statues using one or more filter predicates. SFM uses this API to fetch a series of public statues per the parameters mentioned in the filters. The output genertaed by filterstream is stored in files, the path for the output files is mentioned at the time of the installation.The three categories, which can be passed as the parameters for filtering the tweets are :

Words - Returns public statues containing the words mentioned in this parameter.    

People - Returns public stream on the basis of usernames mentioned in this parameter.

Location- Returns public stream in a particular geographic location mentioned in this parameter.
          This parameter is not upgraded as yet, hence should not be used.

To run:
Fetch and save to file       
     ./manage.py filterstream –save

View samples on console
     ./manage.py filterstream

Automated filter sample fetch
      You need to follow the supervisord installation and configuration settings. (LINK)

Detailed API explanation: 
https://stream.twitter.com/1.1/statuses/filter.json

organizedata
------------
The filterstream and streamsample produces gigs of data in numerous file.Organizedata is a feature in SFM which enhances the directory structure for storing these files.The nomenclature of the output files contains the date and day timestamp for each file.This timestamp is then utilized to form a directory structure such that, each file is organized in directories per their type, year, month and then date.

To run:

Organize the tons of files in sub-directories:
    ./manage.py organizedata

fetch_urls
----------
Fetch_urls is a feature in SFM, which allows you to store the urls in every tweet explicitly.You can view the expanded urls at admin page, under the twitteruseritemurl.
Fetch_urls also provides you with options to mention as the criteria to fetch these urls. The options available are:

1.Startdate -- The earliest date from where you want to fetch the urls

2.Enddate -- The latest date, untill which you want to fetch the urls

3.twitteruser -- The specific twitter username you want to fetch the url for

4.limit -- the limit in integers as to how many urls you will like to fetch

5.refetch -- refetch the fetched urls.

To run:
    ./manage.py fetch_urls 

export_csv
----------
SFM allows you to save the tweets from every twitter username, in the form of csv reports.A detailed explanation of the report can be found at the Data Dictionary at the about page in SFM UI http://gwsfm-prod.wrlc.org/about/   
The report can be downloaded from the SFM UI directly, otherwise you can use the command as mentioned below to extract reports.The various options which can be given as the criteria to extract the report are:

1.start-date -- returns the tweets starting from the specified date.

2.end-date -- returns the tweets ending at the specified date.

3.twitter-user -- returns all the tweets for the specified date

4.set-name -- allows you ro customise the file name of the csv report.

To run:

extract the CSV report
       ./manage.py export_csv

createconf
----------
Createconf command is used to create the configuration files.These conf files are the sub-processes picked up by Supervisord.By default, Supervisord is configuired to initiate the streamsample subprocess, while the filtrestream conf files are dynamically added as sub-process under supervisord. This command is signaled to execute when a twitter filter is added to the system. 

To run manually:

    ./manage.py createconf --twitter-filter

Read more about the superviord conf:
LINK 
