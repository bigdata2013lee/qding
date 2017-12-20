# -*- coding: utf-8 -*-
import re

from django.core.management.base import BaseCommand
import os, sys, time
import subprocess

from conf.qd_conf import CONF




def local(cmd, log=False):
    if log: print('[LOCAL]: ' + cmd)

    process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate()

    if stderrdata:
        print('Error:' + stderrdata.decode('utf8'))
        sys.exit()

    if stdoutdata:
        print(stdoutdata.decode('utf8'))

    return stdoutdata.decode('utf8')

def _list_process():

    print('\n======== SHOW PYTHON PROCESS =========\n')
    local("ps -ef | grep 'python3 manage.py' | grep -v grep | grep -v 'manage.py project list' ")




def stop_process(pnames=""):
    output = local("""ps aux | grep  -e 'runscript' | grep -v 'grep'  | awk '{print  $14 " " $2}'  """)

    process_m_pid = {}
    find = re.findall("^(\w+)\s+(\d+)", output, re.M)

    for item in find:
        process_m_pid[item[0]] = item[1]

    for pname in re.findall("(\w+)\s*", pnames) or process_m_pid.keys():
        pid = process_m_pid.get(pname, "")
        if not pid:
            print("未发现进程%s" %pname)
            continue

        local("kill -9 %s" %pid)


def restart_process(pnames=""):
    stop_process(pnames=pnames)

    _process_name_list = re.findall("(\w+)\s*", pnames) or CONF.get("default_process", [])

    for pname in _process_name_list:
        subprocess.call("nohup python3 manage.py  runscript %s >> %s/log/main_out.log &" %(pname, CONF['app_home']), shell=True)







def help():
    description = """
        #使用uwsgi方式启动web服务，请使用下面命令
        uwsgi --ini     ./conf/wsgi.ini
        uwsgi --stop    ./pids/wsgi.pid
        uwsgi --reload  ./pids/wsgi.pid

        stop_process            : stop script process
        restart_process         : restart script process

        list                    : list all python process
        help                    : help information

    """
    print(description)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # positional arguments
        parser.add_argument('action', nargs='?', default='help')
        parser.add_argument('--pnames', nargs='?', default='')


    def handle(self, *argv, **options):

        if options['action'] == 'stop_process':
            stop_process(options.get("pnames", ""))

        elif options['action'] == 'restart_process':
            restart_process(options.get("pnames", ""))

        elif options['action'] == 'list':
            _list_process()

        else:
            help()
