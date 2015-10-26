FROM ubuntu:12.04
MAINTAINER Justin Littman <justinlittman@gwu.edu>

RUN apt-get update && apt-get install -y \
    python-dev \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    supervisor \
    git \
    python-pip \
    apache2 \
    libapache2-mod-wsgi \
    wget \
    cron
#Upgrade pip
RUN pip install -U pip
#This pre-fetches the most recent requirements.txt.
ADD https://github.com/gwu-libraries/social-feed-manager/raw/master/requirements.txt /opt/sfm-setup/
RUN pip install -r /opt/sfm-setup/requirements.txt
#This is used to automatically create the admin user.
RUN pip install django-finalware==0.0.2
#These will be copied over into the app by invoke.sh.
ADD local_settings.py /tmp/
ADD wsgi.py /tmp/
#Enable sfm site
ADD apache.conf /etc/apache2/sites-available/sfm
RUN a2ensite sfm
#Disable pre-existing default site
RUN a2dissite 000-default
#Configure supervisor
ADD supervisord.conf /etc/supervisor/
RUN mkdir /var/log/sfm
RUN mkdir /var/sfm && chmod ugo+w /var/sfm
VOLUME /var/sfm
RUN mkdir /var/supervisor.d && chown www-data:www-data /var/supervisor.d
ADD invoke.sh /opt/
RUN chmod +x /opt/invoke.sh
#Install appdeps to allow checking for application dependencies
WORKDIR /opt/sfm-setup
RUN wget -L --no-check-certificate https://github.com/gwu-libraries/appdeps/raw/master/appdeps.py
#Cron
ADD crons.conf /tmp/
RUN crontab /tmp/crons.conf
CMD ["/opt/invoke.sh"]
EXPOSE 80
