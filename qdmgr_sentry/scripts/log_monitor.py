# --*-- coding:utf8 --*--
import subprocess
import os
import datetime
'''
nginx_log_dir = '%s%s%s%s%s%s' % (os.sep, 'data', os.sep, 'nginx_log', os.sep, 'tx-error.log')
command = "tail -10 %s | awk '{print $1,$2}'" % nginx_log_dir
p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
time_list = p.stdout.readlines()

now = datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d %H:%M")
time_list = [t.decode('utf8').strip() for t in time_list]
print(time_list)
print(now)
for t in time_list:
    if now in t:
        print(t)
'''
import sys
import threading
from requests.sessions import Session
session = Session()
sys.path.insert(0, '/data/qding/qdmgr_sentry')

url = 'http://www.qding.cloud/basedata_api/Basedata_Bj_App_User_Api/get_app_user_can_open_door_list/'
params = {"outer_app_user_id": "8aa57dca4fcfaf9f01508423b56c0109"}
i = 0

def ff():
    response = session.post(url, data=params).content.decode('utf8')
    print(response)


def fff():
    from apps.common.api.basedata_api import Basedata_Bj_App_User_Api
    Basedata_Bj_App_User_Api().get_app_user_can_open_door_list(**params)

while i < 100:
    t = threading.Thread(target=ff, args=())
    t.setDaemon(False)
    t.start()
    i+=1

'''
class A(type):
    def __new__(cls, *args, **kwargs):
        print('i am new a')
        return super(cls, A).__new__(cls, *args, **kwargs)

    def __init__(self, what, bases=None, dict=None):
        print('i am init a')

    def __call__(self, *args, **kwargs):
        print('i am call a')


class B():
    pass
'''
