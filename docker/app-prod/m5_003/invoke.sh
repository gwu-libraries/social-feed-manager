#!/bin/bash
echo "Waiting for db"
python /opt/social-feed-manager/appdeps.py --wait-secs 30 --port-wait db:5432
if [ "$?" = "1" ]; then
    echo "Problem with application dependencies."
    exit 1
fi

echo "Writing local_settings"
echo "env={}" > /opt/social-feed-manager/sfm/sfm/local_settings.py
env | grep 'SFM_\|\DB_' | sed 's/\(.*\)=\(.*\)/env["\1"]="\2"/' >> /opt/social-feed-manager/sfm/sfm/local_settings.py
cat /tmp/local_settings.py >> /opt/social-feed-manager/sfm/sfm/local_settings.py

echo "Syncing db"
/opt/social-feed-manager/sfm/manage.py syncdb --noinput

echo "Migrating db"
/opt/social-feed-manager/sfm/manage.py migrate --noinput

echo "Starting supervisord"
/etc/init.d/supervisor start

echo "Starting cron"
cron

echo "Running server"
#Not entirely sure why this is necessary, but it works.
/etc/init.d/apache2 start
#Make sure apache has started
/etc/init.d/apache2 status
while [ "$?" != "0" ];  do
    echo "Waiting for start"
    sleep 1
    /etc/init.d/apache2 status
done
echo "Stopping server"
/etc/init.d/apache2 graceful-stop
#Make sure apache has stopped
/etc/init.d/apache2 status
while [ "$?" = "0" ];  do
    echo "Waiting for stop"
    sleep 1
    /etc/init.d/apache2 status
done
echo "Starting server again"
apachectl -DFOREGROUND
