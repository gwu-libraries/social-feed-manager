social feed manager
===================

A django application for managing multiple feeds of social media data.

Developed at the GWU Libraries in Washington, DC, USA.

See also LICENSE.txt.


installation
------------

* developed using python 2.7 and postgresql-9.1 on osx for deployment
  on ubuntu lts; ymmv.

* get this code:

    % git clone http://github.com/gwu-libraries/ADDME

* create and activate a virtualenv:
  
    % virtualenv --no-site-packages ENV
    % source ENV/bin/activate

* install requirements

    % pip install -r requirements.txt

* add and edit local_settings.py

    % cp sfm/local_settings.py.template sfm/local_settings.py

* create local database as you specified in local_settings.py

