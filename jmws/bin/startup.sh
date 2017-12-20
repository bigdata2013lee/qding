#! /bin/bash

app_home='/opt/jmws'
cd ${app_home}
python3 manage.py migrate
sleep 1
uwsgi --ini  ./bin/wsgi.ini
sleep 1

supervisord -c  ${app_home}/bin/supervision.ini


