FROM gwul/sfm_app:m5_003
MAINTAINER Justin Littman <justinlittman@gwu.edu>

#Enable SSL
RUN a2enmod ssl
RUN a2enmod rewrite
ADD apache.conf /etc/apache2/sites-available/sfm
EXPOSE 80 443
