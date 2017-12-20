# --*-- coding: utf8 --*--
import time
from apps.common.utils.redis_client import rc


def sync_base_data():
    from apps.basedata.process.sync_bj_data_api import sync_project_data
    while True:
        try:
            project_id = rc.got("sync_project_data", "spop")
            if not project_id:
                time.sleep(1)
            else:
                sync_project_data(project_id)
        except Exception as e:
            pass


