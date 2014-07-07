Using Supervisord to Manage Streaming Filters
=============================================

As of release m4_002, Social Feed Manager uses `supervisord
<http://supervisord.org/>`_ to manage the
filterstream and streamsample processes.  As streaming processes,
these are intended to be run on a continuous, ongoing basis, to collect
tweets over time.  Supervisord is a process control system that, among
other features, manages the SFM streaming processes independently from the
SFM web application, and can restart these processes if they fail or after
a system reboot.

Twitterfilters and/or streamsample *can* still be run independently of
supervisord if desired (e.g. for testing), by invoking them at the command
line as :doc:`management commands </mgmt_commands>`.

Supervisord is installed as part of the standard SFM installation; it is
one of SFM's ubuntu package dependencies.  However, it must be configured
in order to use filterstreams.

To configure supervisord for SFM:

edit ``/etc/supervisor/supervisord.conf``. Look for the
``[include]`` section (in a new instance of supervisor, this is
usually at the bottom) and add ``supervisor.d/*.conf`` to the
space-separated list of ``files``:
   
       ``files = /etc/supervisor/conf.d/*.conf <PATH_TO_YOUR_SFM>/sfm/sfm/supervisor.d/*.conf``

create a ``/var/log/sfm`` directory. The supervisor-supervised
processes will write log files to this directory.

.. code-block:: none

        $ sudo mkdir /var/log/sfm

edit local_settings.py to set DATA_DIR to the directory where you
want stream output stored. Set SUPERVISOR\_PROCESS\_OWNER to a user
who has rights to write to ``/var/log/sfm``. You may also wish to
adjust SAVE\_INTERVAL\_SETTINGS, which controls how often sfm will
save data to a new file (default is every 15 minutes, specified in
```settings.py```).

set the permissions on the ``sfm/sfm/supervisor.d`` directory to
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


Streamsample setup
------------------
A template streamsample configuration file "streamsample.conf.template" is
included in the SFM distribution.  To set up a streamsample process managed by
supervisor:

Browse to the supervisord.d directory and copy streamsample.conf.template
to streamsample.conf

.. code-block:: none

   $ cd sfm/sfm/supervisor.d
   $ cp streamsample.conf.template streamsample.conf

Edit streamsample.conf to use the path to your sfm project, the value of the PATH environment variable set within your virtualenv, and to use your preferred system user account (to avoid having the output files owned by root).

To have supervisor refresh its list of configuration files and start the
streamsample process, first run supervisorctl:

.. code-block:: none
   
     $ sudo supervisorctl

If you don't see a line that reads something like:

       streamsample                     RUNNING    pid 889, uptime 21:45:25

then at the supervisor prompt, run 'update' to reload the config files:

.. code-block:: none

     $ supervisor> update

Running update should result in the following message:

       streamsample: added process group

Now verify that streamsample has been started by viewing the status of
the processes:

.. code-block:: none

     $ supervisor> status

This should result in a list of processes which includes streamsample,
for example:

       streamsample                     RUNNING    pid 889, uptime 21:45:25

To stop the streamsample process, run supervisorctl and use the command

.. code-block:: none

     $ supervisor> stop streamsample



Filterstream setup
------------------

TwitterFilters in SFM are intended to create filterstream Twitter processes.

While streamsample must be started and stopped using supervisorctl,
supervisor's management of TwitterFilter processes is mediated by the SFM
application.

SFM creates configuration files for filterstream processes when an administrative
user adds new TwitterFilters in SFM.  The files are created in the
sfm/sfm/supervisor.d directory.  SFM takes care of updating supervisor so that
it starts the new filterstream process.

If an administrative user modifies an existing, active TwitterFilter, SFM
deletes the old configuration file for that TwitterFilter's filterstream
process, writes a new configuration file containing the TwitterFilter's updated
parameters, and restarts the filterstream process.

If an administrative user deactivates or deletes a TwitterFilter, SFM
deletes the configuration file for that TwitterFilter's filterstream process,
and stops the filterstream process.


OAuth constraints
-----------------

To avoid triggering the Twitter API's rate limiting constraints, every
SFM streaming connection must use a different set of Twitter credentials.
SFM does not allow active filterstreams to run using the same Twitter
credentials as streamsample, or as any other active filterstream.

The streamsample process connects to the Twitter API using the
TWITTER_DEFAULT_USERNAME set in local_settings.py.  Each Filterstream process
connects to the Twitter API using the User configured in its TwitterFilter.
