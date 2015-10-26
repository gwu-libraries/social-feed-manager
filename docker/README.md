Docker for SFM
---------------------

Requirements
===========
1.  [Docker](https://docs.docker.com/installation/)
2.  [Docker Compose](https://docs.docker.com/compose/install/) Docker Compose

Development configuration
====================
In this configuration, the code lives outside the app container, but is shared with the container.  This means changes made to the code are used by the instance of SFM running in the container.

1.  Check out the code somewhere.
2.  Copy example.dev.docker-compose.yml to docker-compose.yml.

        cd social-feed-manager/docker
        cp example.dev.docker-compose.yml docker-compose.yml

3.  In docker-compose.yml:

    * update the SFM_TWITTER_* environment variables.
    * update the location of the code (from `~/Data/sfm/social-feed-manager`).

See app-dev/local_settings.py for additional configuration that can be made using environment variables.

4.  Up:

        docker-compose up -d

SFM will now be available at http://localhost:8000/sfm.  (Unless you're on OS X -- use `docker-machine ip default` to determine the ip to use instead of localhost.)

Latest development configuration
===========================
This configuration provides the latest code committed to the SFM master branch.  It is automatically updated when a new commit is made.

1.  Download docker-compose.yml:

        curl -L https://github.com/gwu-libraries/social-feed-manager/raw/master/docker/example.master.docker-compose.yml > docker-compose.yml

    Or if you already have the code checked out, copy example.master.docker-compose.yml to docker-compose.yml.

        cd social-feed-manager/docker
        cp example.latest.docker-compose.yml docker-compose.yml

2.  In docker-compose.yml:

    * update the SFM_TWITTER_* environment variables.

See app-latest/local_settings.py for additional configuration that can be made using environment variables.

3.  Up:

        docker-compose up -d

SFM will now be available at http://localhost:8000/sfm.  (Unless you're on OS X -- use `docker-machine ip default` to determine the ip to use instead of localhost.)

Production configuration
==================
This configuration provides released instances of SFM.  Additional releases will be added.

In this configuration, the data directory is a host volume.

1.  Download docker-compose.yml:

        curl -L https://github.com/gwu-libraries/social-feed-manager/raw/master/docker/example.prod.docker-compose.yml > docker-compose.yml

    Or if you already have the code checked out, copy example.prod.docker-compose.yml to docker-compose.yml.

        cd social-feed-manager/docker
        cp example.prod.docker-compose.yml docker-compose.yml

2.  Create the directory that will be mounted as a host volume:
       
        mkdir /sfm-data
        chmod ugo+w /sfm-data

3.  In docker-compose.yml:

    * update the SFM_TWITTER_* environment variables.
    * update the host volume (from `/sfm-data`).
    * update the [tag](https://registry.hub.docker.com/u/gwul/sfm_app/tags/manage/) of the sfmapp image to the desired release.

See app/*/local_settings.py for additional configuration that can be made using environment variables.

4.  Up:

        docker-compose up -d

SFM will now be available at http://localhost/sfm.  (Unless you're using OS X -- use `docker-machine ip default` to determine the ip to use instead of localhost.)

### Production configuration with HTTPS
A variation of the production configuration that uses HTTPS is available.  The HTTPS images are the same as the production images with _https appended (e.g., gwul/sfm_app:m5_002_https).

The instructions are the same as above, except:
* The name of the example docker-compose.yml is example.prod-https.docker-compose.yml.
* When updating docker-compose.yml, the location of the SSL certificate and key files on the host system should be provided.  For guidance on creating the key file and certificate file in an Ubuntu 12 environment, see https://help.ubuntu.com/12.04/serverguide/certificates-and-security.html (follow all steps, including shuffling the secure and insecure keys).

All HTTP requests (port 80) will be redirected to HTTPS (port 443).

Additional notes
============
* The SFM admin account is "sfmadmin" and password is "password".  (This can be
changed -- see local_settings.py.)
* Differences from a typical SFM deploy to be aware of:
    * The postgres instance comes from the docker image (https://registry.hub.docker.com/_/postgres/),
not the postgres debian package.
    * The postgres instance is not restricted in the pg-hba.conf file.  Rather, the
access to postgres is restricted at the container level.  Only linked containers
can connect to the postgres container.
    * For postgres, the postgres user is used instead of an SFM user.
    * VirtualEnv is not used (since python is isolated by the container).
    * Everything is run as root.
    * Supervisord is running.
* The sfm_app container shares the `/var/sfm` volume (except in the production configuration).
