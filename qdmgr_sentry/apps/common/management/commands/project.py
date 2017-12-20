# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
import logging
import sys

logger = logging.getLogger('qding')


def initdata():
    from apps.common.initdata import Basedata_Geo_Initdata
    from apps.common.initdata import Web_User_Initdata


def collect():
    try:
        from apps.common.utils.redis_client import Redis_To_Mongo
        Redis_To_Mongo().start_collect()
    except Exception as e:
        logger.exception("exception:%s" % e)


def monitor():
    try:
        from apps.common.utils.redis_client import Redis_To_Mongo
        Redis_To_Mongo().start_monitor()
    except Exception as e:
        logger.exception("exception:%s" % e)


def update_process():
    try:
        from apps.common.utils.redis_client import Redis_To_Mongo
        Redis_To_Mongo().start_update_process()
    except Exception as e:
        logger.exception("exception:%s" % e)


def start_api_test():
    from api_test import test_all
    test_all()




def help():
    print("""
inidata             : init system data,include web_user,geo_data,gate
collect             : collect redis data to mongodb
monitor             : monitor brake
update_process      : update_process
update_db           : update_db
help                : help information
""")


class Command(BaseCommand):
    def handle(self, *argv, **options):
        if len(argv) < 1:
            help()
            sys.exit()
        if argv[0] == 'initdata':
            initdata()
        elif argv[0] == 'collect':
            collect()
        elif argv[0] == 'monitor':
            monitor()
        elif argv[0] == 'update_process':
            update_process()
        elif argv[0] == 'test':
            start_api_test()
        else:
            help()
