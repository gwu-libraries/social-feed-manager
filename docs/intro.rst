.. Social Feed Manager Introduction file

Introduction
============

Social Feed Manager is open source software for locally capturing public data from Twitter. 
It makes it possible for scholars, students, archivists, and librarians to:

- identify, select, collect, and preserve "at risk" social media data
- gather datasets of tweets in bulk for analysis in other software packages
- fill gaps in special collections
- archive the social media activity of their library or institution.

The software connects to Twitter's approved public APIs to collect tweets by specific users, search current tweets by keyword, and filter by geolocation. We hope to add other social media platforms in the future.  

Current uses at George Washington University
--------------------------------------------
- The University Archives is gathering tweets by university offices and student organizations, capturing an aspect of student life whose main online presence is on social media
- Faculty in the School of Media and Public Affairs are studying how journalists, activist organizations, and members of Congress tweet
- Students in digital journalism are learning how to analyze tweets to inform reporting
- Computer science faculty are using tweet datasets to train machine learning algorithms

Features
--------
- Collects tweets account by account
- Queries streaming APIs by keyword, user, and geolocation
- Captures Twitter's sample stream (currently ~0.5-1% of tweets)
- Manages multiple streams reliably
- Respectful of Twitter rate limits
- Groups tweets into sets for easier management
- CSV export, which can be uploaded into analysis software of the researcher's choice
- Web-based interfaces for researchers / data users and administrators
- Command-line updates for application administrator
- Streaming data output to compressed rolling files in date/time hierarchy

Technical and staffing considerations
-------------------------------------
Social Feed Manager is locally hosted and requires a system administrator to set up and manage the application in a Linux (Ubuntu 12.04) environment.  Storage requirements vary depending on usage of the application: collecting data account-by-account requires less storage than connecting to the streaming APIs, which accumulates large files. 

Archivists, librarians and other service administrators, as determined by the library, use a web-based interface to add 
new Twitter users, specify keyword queries, and create sets of accounts. Researchers may directly download user timeline data 
from the web interface after signing into the site from an institutional IP address and using their own Twitter credentials. Currently, all captured user timeline data is available in the researcher interface and is not separated by researcher account. Accessing files generated from the streaming APIs requires mediation by a system administrator.

Development and community
-------------------------
Social Feed Manager was developed at The George Washington University Libraries in 2012 as a prototype application and is now being supported by multiple developers and an IMLS Sparks! Innovation Grant.[1] Several libraries and archives have installed it and are providing feedback to help prioritize development of new features. 

The software is available for use, study, copying, and modification under a free and open source software license (MIT license). We welcome others to become involved in the project and contribute to the code.

Resources
^^^^^^^^^
`Social Feed Manager on Github
<https://github.com/gwu-libraries/social-feed-manager>`_

`Google Group (updates about new releases and discussion of features)
<https://groups.google.com/forum/#!forum/sfm-dev>`_

[1] Institute of Museum and Library Services Grant LG-46-13-0257
