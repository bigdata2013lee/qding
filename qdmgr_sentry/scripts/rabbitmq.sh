#! /bin/bash

rpm -ivh http://dl.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
yum -y install erlang
yum -y install rabbitmq-server

chkconfig rabbitmq-server on
service rabbitmq-server start