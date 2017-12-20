# -*- coding:utf8 -*-
import traceback
from apps.basedata.classes.Basedata_Project import Basedata_Project
from apps.basedata.classes.Basedata_Group import Basedata_Group
from apps.basedata.classes.Basedata_Build import Basedata_Build
from apps.basedata.classes.Basedata_Unit import Basedata_Unit
from apps.brake.classes.Brake_Machine import Brake_Machine
from apps.web.classes.Web_User import Web_User
from apps.brake.classes.Brake_Version import Brake_Version
from apps.brake.classes.Brake_Card import Brake_Card
from apps.common.utils.redis_client import rc


def update_web_user():
    for w in Web_User.objects():
        user_type = getattr(w, "user_type", 0) or 0

        def __check(t1, t2, t3, role_list):
            if user_type == t1:
                w.role_list = role_list
                w.access = 4
            elif user_type == t2:
                w.role_list = role_list
                w.access = 2
                city_id_list = []
                project_list = getattr(w, 'project_list', []) or []
                for p in project_list:
                    city_id = getattr(p, "outer_city_id", "") or ""
                    if city_id and city_id not in city_id_list: city_id_list.append(city_id)
                w.area = city_id_list
            elif user_type == t3:
                w.role_list = role_list
                w.access = 1
                project_id_list = []
                project_list = getattr(w, 'project_list', []) or []
                for p in project_list:
                    project_id = getattr(p, "outer_project_id", "") or ""
                    if project_id and project_id not in project_id_list: project_id_list.append(project_id)
                w.area = project_id_list

        if user_type == 11:
            w.role_list = [1]
            w.access = 4
        elif user_type in [20, 21, 22]:
            __check(20, 21, 22, [2, 3])
        elif user_type in [30, 31, 32]:
            __check(30, 31, 32, [4])
        elif user_type in [40, 41, 42]:
            __check(40, 41, 42, [3])
            w.password = w.brake_config_password
            w.password_num = w.brake_config_password_num
        area_flag, area, area_str, area_ret = w.check_area(w.area, w.access)
        w.area_str = area_str
        w.save()


def update_brake_version():
    for version in Brake_Version.objects(status="1"):
        project_list = getattr(version, "project_list", []) or []
        for i in range(len(project_list)):
            project_dict = project_list[i]
            project_obj = Basedata_Project.objects(province=project_dict['province'], city=project_dict['city'], project=project_dict['project']).first()
            project_list[i]['outer_project_id'] = project_obj.outer_project_id
        version.project_list = project_list
        version.save()


def update_brake_machine():
    for brake in Brake_Machine.objects(__raw__={"modify_status": {"$ne": 1}}):
        try:
            province = brake.position['province']
            city = brake.position['city']

            position = {
                "province": province,
                "city": city,
                "level": brake.position['level'],
            }

            project_list = []
            for project_dict in brake.position['project_list']:
                project = project_dict['project']
                raw_query = {
                    "province": province,
                    "city": city,
                    "project": project
                }
                project_obj = Basedata_Project.objects(__raw__=raw_query).first()
                pd = {
                    "project": project,
                    "outer_project_id": project_obj.outer_project_id,
                }
                group_list = []

                for group_dict in project_dict.get('group_list', []):
                    group = group_dict.get('group', '')
                    gd = {
                        "group": group,
                        "outer_group_id": "",
                    }
                    if group:
                        raw_query = {
                            "province": province,
                            "city": city,
                            "project": project,
                            "group": group
                        }
                        group_obj = Basedata_Group.objects(__raw__=raw_query).first()
                        gd.update({
                            "outer_group_id": group_obj.outer_group_id
                        })

                    build_list = []
                    for build_dict in group_dict['build_list']:
                        build = build_dict['build']
                        raw_query = {
                            "province": province,
                            "city": city,
                            "project": project,
                            "build": build
                        }
                        if group: raw_query.update({"group": group})
                        build_obj = Basedata_Build.objects(__raw__=raw_query).first()
                        bd = {
                            "build": build,
                            "outer_build_id": build_obj.outer_build_id,
                        }
                        unit_list = []
                        unit_dict_list = []
                        for unit in build_dict['unit_list']:
                            raw_query = {
                                "province": province,
                                "city": city,
                                "project": project,
                                "build": build,
                                "unit": unit
                            }
                            if group: raw_query.update({"group": group})
                            unit_obj = Basedata_Unit.objects(__raw__=raw_query).first()
                            ud = {
                                "unit": unit_obj.unit,
                                "project_group_build_unit_id": unit_obj.unit_id,
                                "password_num": unit_obj.password_num if unit_obj.password_num else 1500,
                            }
                            unit_list.append(unit)
                            unit_dict_list.append(ud)
                        bd.update({
                            "unit_list": unit_list,
                            "unit_dict_list": unit_dict_list
                        })
                        build_list.append(bd)
                    gd.update({
                        "build_list": build_list
                    })
                    group_list.append(gd)

                pd.update({
                    "group_list": group_list
                })
                project_list.append(pd)

            position.update({
                "project_list": project_list
            })

            brake.position = position
            brake.position_str = Brake_Machine.make_position_str(position, brake.gate_info)
            brake.modify_status = 1
            brake.save()
        except Exception as e:
            print(brake.id)
            print(raw_query)
            print(traceback.format_exc())
            return
    for k in rc.cnn.keys("api_cache:Brake_Machine.get_project_brake*"): rc.cnn.delete(k)


def update_brake_card():
    for card in Brake_Card.objects():
        card_area_list = getattr(card, "card_area", []) or []
        black_door_list = getattr(card, "black_door_list", []) or []

        for i in range(len(card_area_list)):
            card_area_dict = card_area_list[i]
            project_obj = Basedata_Project.objects(project_id=card_area_dict['project_id']).first()
            card_area_list[i]['outer_project_id'] = project_obj.outer_project_id

        tmp = []
        for j in range(len(black_door_list)):
            if isinstance(black_door_list[j], dict): continue
            if not isinstance(black_door_list[j], Brake_Machine):
                black_door_list[j] = Brake_Machine.objects(id=black_door_list[j]).first()
            if black_door_list[j]:
                tmp.append(black_door_list[j].get_brake_info())

        card.black_door_list = tmp
        card.card_area = card_area_list
        card.set_door_list()
        card.save()


def run():
    # update_web_user()
    # update_brake_version()
    # update_brake_machine()
    update_brake_card()

