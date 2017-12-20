# --*-- coding: utf8 --*--
import time
from apps.basedata.classes.Basedata_BJ_App_User import Basedata_BJ_App_User
from apps.common.utils.redis_client import rc


def update_app_user():
    while True:
        try:
            phone = rc.got("update_app_user", "spop")
            if not phone:
                time.sleep(1)
            else:
                do_update_app_user_door_list_by_phone(phone)
        except Exception as e:
            pass


def do_update_app_user_door_list_by_phone(phone):
    app_user_list, ret_str = Basedata_BJ_App_User(phone=str(phone)).get_app_user_by_phone(1498724908)
    app_user_list = [app_user_list] if isinstance(app_user_list, Basedata_BJ_App_User) else app_user_list
    if not app_user_list: app_user_list = []
    for app_user in app_user_list:
        app_user.set_app_user_from_bj(app_user.outer_project_id)


