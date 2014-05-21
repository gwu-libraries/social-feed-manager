
Supervisord
===========

If you want to capture streams of filtered queries or sample data from Twitter’s
spritzer feed continually, you might want a process supervisor to ensure
the process remains active and is restarted automatically after system
reboots and the like, supervisord does that for sfm.

Getting started
---------------

Supervisord is already mentioned as a default package to be installed when SFM is installed into your system, if you have not done so, then install supervisord explicitly as mentioned below.

Install supervisord using either of the mentioned below:

* apt-get

.. code-block:: none

     $ sudo apt-get install supervisor

This will install the supervisord, and you will need to create a
supervisord configuration file. Invoke the following command under root
access to set up the configuration file:

* setup configuration file

.. code-block:: none

     $ echo_supervisord_conf > /etc/supervisord.conf

Once the configuration file for supervisord is set up, you will need to
modify it per the SFM requirements.

For more information on installing supervsiord: `Supervisord explained`_.

.. _Supervisord explained: http://supervisord.org/installing.html


SFM-supervisord setup
---------------------

-  edit ``/etc/supervisor/supervisord.conf``. Look for the
   ``[include]`` section (in a new instance of supervisor, this is
   usually at the bottom) and add ``supervisor.d/*.conf`` to the
   space-separated list of ``files``:
   
       ``files = /etc/supervisor/conf.d/*.conf <PATH_TO_YOUR_SFM>/sfm/sfm/supervisor.d/*.conf``

-  create a ``/var/log/sfm`` directory. The supervisor-supervised
   processes will write log files to this directory.

.. code-block:: none

        $ sudo mkdir /var/log/sfm

-  edit local_settings.py to set DATA_DIR to the directory where you
   want stream output stored. Set SUPERVISOR\_PROCESS\_OWNER to a user
   who has rights to write to ``/var/log/sfm``. You may also wish to
   adjust SAVE\_INTERVAL\_SETTINGS, which controls how often sfm will
   save data to a new file (default is every 15 minutes, specified in
   ```settings.py```).

-  set the permissions on the ``sfm/sfm/supervisor.d`` directory to
   allow the sfm process owner to write to it. Since the sfm process may
   be running as a different user than the owner of the directory, we’re
   going to create a new ‘sfm’ group:

.. code-block:: none

      $ sudo groupadd sfm

and add the sfm process owner to this group. Edit ``/etc/group``:

.. code-block:: none

     $ sudo vi /etc/group

You should see a new line at the end that looks something like this:

       ``sfm:x:<a group number>:``

Add the process owner, and optionally add your own user to this group:

       ``sfm:x:<a group number>:www-data,<your user name>``

Now change the group of the ``supervisor.d`` directory to sfm:

.. code-block:: none

   $ sudo chgrp sfm sfm/sfm/supervisor.d

Once the supervsiord.conf file and the respective permissions are setup, supervsiord needs to be configured to manage the sub-process under it.

RUN Supervisord
---------------
Supervisord is a deamon process, yet it needs to be initiated manually first time after the installation is complete. 

First time run:

.. code-block:: none

    $ sudo service supervisord start

It should show something like this

   "Starting supervisor: supervisord."

supervisord also has a command-line option to control its subprocess, supervisorctl can be used to check on the status of a process. To start supervisorctl you can :

.. code-block:: none
 
     $ sudo supervisorctl 

For more information on `Supervisorctl`_.
    
.. _Supervisorctl: http://supervisord.org/running.html#running-supervisorctl

Streamsample setup
------------------
By Default, a template streamsample configuration file "streamsample.conf.template" is present in SFM, this can be used to set up the configuration file for streamsmaple subprocess ``supervisor.d/streamsample.conf``

* browse to the supervisord.d directory:

.. code-block:: none

   $ cd sfm/sfm/supervisor.d
   $ cp streamsample.conf.template streamsample.conf

and edit streamsample.conf to use the path to your sfm project, the value of the PATH environment variable set within your virtualenv, and to use your preferred system user account (to avoid having  the output files owned by root).

* to verify that supervisord detected the new configuration file and has started the process, run supervisorctl:

.. code-block:: none
   
     $ sudo supervisorctl

* if you don't see a line that reads something like:

       streamsample                     RUNNING    pid 889, uptime 21:45:25

then at the supervisor prompt, run 'update' to reload the config files:

.. code-block:: none

     $ supervisor> update

and start streamsample

.. code-block:: none

     $ supervisor> start streamsample


Filterstream setup
------------------
Supervisord can be configured to manage filterstream as well. The configuration file for filterstream is created dynamically when a new Twitter Filter is added to SFM.The createconf management command is executed implicitly to create the filtersteam conf files.

As you create, modify, activate, and deactivate TwitterFilters using the admin UI, SFM creates or deletes a supervisor configuration file for each TwitterFilter. It will also delete a configuration file when you mark a TwitterFilter as inactive. However, if you have pre-existing, active TwitterFilters which were created prior to SFM release m4_001, you will need to run the ```createconf``` command manually to create supervisor configuration files for your active TwitterFilters.

* With your virtualenv activated, execute

.. code-block:: none

    $ ./manage.py createconf

Currently supervisor does not appear to automatically detect additions/deletions/changes to the filterstream configuration files that occur when you run createconf and/or make changes to TwitterFilter.To "refresh" supervisor, execute

.. code-block:: none

     $ sudo supervisorctl update

.. important:: The streamsample includes something like 0.5-1% of all tweets and deletes, which as of February 2014 means roughly three million or so items combined. Filters can create a similarly large amount of data. These files add up quickly, so consider your available disk space, and consider using the organizedata(LINK) management command in a cron job to sort generated files into date-based directories regularly.

.. attention:: Filterstream and streamsample cannot run under the same OAUth credentials. SFM handles this implicitly, it doesnt allow you to add filters under the same credential as streamsample. Streamsample is configured to use the OAuth credentials mentioned in the local_settings.py. If you ever get an http error while using streams, then you need to check if either are running under same credentails and stop one of the streams explicitly.
