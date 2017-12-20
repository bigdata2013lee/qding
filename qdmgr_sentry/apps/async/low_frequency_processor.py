# --*-- coding: utf8 --*--
import pickle
import time
from apps.basedata.classes.Basedata_Unit import Basedata_Unit
from apps.brake.classes.Brake_Machine import Brake_Machine
from apps.brake.classes.Brake_Pass import Brake_Pass
from apps.common.utils.redis_client import rc


def update_process():
    while True:
        try:
            update_dict = rc.got("update_process", "spop")
            if not update_dict:
                time.sleep(1)
            else:
                for k, v in update_dict.items():
                    do_process(k, v)
        except Exception as e:
            pass


def do_process(process_type, process_value):
    if process_type == 'refresh_project_data':
        return do_refresh_project_data(process_value)
    elif process_type == 'update_project_pass_count':
        return do_update_project_pass_count(process_value)


def do_refresh_project_data(project_id):
    unit_obj = Basedata_Unit.objects(outer_project_id=str(project_id)).first()
    if not unit_obj: return False
    name = "%sinit_project_data" % project_id
    value = unit_obj.get_project_dict()
    rc.set(name, pickle.dumps(value))
    return value


def do_update_project_pass_count(project_pass_count_dict):
    province = project_pass_count_dict['province']
    city = project_pass_count_dict['city']
    project = project_pass_count_dict['project']
    day = project_pass_count_dict['day']
    keys = "%s#%s#%s#%s" % (day, province, city, project)
    bp = Brake_Pass(brake_machine=Brake_Machine())
    ret = bp.set_project_day_pass_count(province, city, project, day)
    rc.set(keys, pickle.dumps(ret))
    return ret

