# --*-- coding: utf8 --*--
import time
import pickle
from apps.common.utils.redis_client import rc
from apps.common.utils.xutil import get_key_from_dict


def dump_data():
    from apps.common.api.brake_api import Brake_Machine_Api
    while True:
        try:
            kargs = rc.got("dump_data_process", "spop")
            if not kargs:
                time.sleep(1)
            else:
                kargs = pickle.loads(kargs)
                # result = Brake_Machine_Api().get_brake_machine_by_filter(**kargs)
                result = Brake_Machine_Api().get_brake_machine_by_project_id_list(**kargs)
                brake_machine_list = result['data'].get('brake_machine_list', [])
                brake_list = result['data'].get('brake_list', [])
                if len(brake_list) != len(brake_machine_list):
                    brake_machine_list = [brake_machine.get_brake_info() for brake_machine in brake_list]
                key = get_key_from_dict(kargs)
                rc.set(key, pickle.dumps(brake_machine_list), 24 * 3600)
        except Exception as e:
            pass
