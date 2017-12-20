#! /bin/bash

app_home='/opt/cloud_talk'
cd ${app_home}/src
python3 manage.py migrate
sleep 1
uwsgi --ini  ./conf/wsgi.ini
sleep 1

supervisord -c  ${app_home}/bin/supervision.ini


