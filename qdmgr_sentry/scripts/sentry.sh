#!/bin/bash 
name="sentry"
ip_port="0.0.0.0:8003"
application_dir="/data/qding/qdmgr_sentry"
uwsgi_ini_file="$application_dir/settings/uwsgi.ini"
pid_file="$application_dir/var/qdmgr_sentry.pid"



function start_sentry(){
    num=`ps -ef|grep -v grep|egrep "$ip_port | python3 manage.py project" |wc -l`
    if [ $num -ne 0 ];then
        echo "$name has runing"
    else
        cd $application_dir
#        uwsgi --ini $uwsgi_ini_file
        nohup python3 manage.py runserver_plus "$ip_port" --threaded --nostatic &>/dev/null &
        nohup python3 manage.py async  &>/dev/null &
        echo "$name is running now"
    fi
}

function stop_sentry(){
#    uwsgi --stop $pid_file
    ps -ef|grep "$ip_port"|grep -v grep|awk '{print $2}'|xargs kill -9
    ps -ef|grep "python3 manage.py async"|grep -v grep|awk '{print $2}'|xargs kill -9
    echo "$name stop"
}


case "$1" in
	start)
	    start_sentry
        ;;
    stop)
        stop_sentry
		;;
	restart)
	    stop_sentry
	    start_sentry
	    ;;
	*)
	    echo "Usage: $name {start|stop|restart}"
	    ;;
esac