# -*- coding:utf-8 -*-
from mongoengine.document import DynamicDocument
from apps.common.classes.Base_Class import Base_Class
from apps.basedata.classes.Basedata_Project import Basedata_Project
from mongoengine.fields import StringField, ListField, IntField
from apps.common.utils.qd_decorator import method_set_rds


class Web_User(DynamicDocument, Base_Class):
    role_list = ListField(default=[])  # 1-系统管理, 2-物业管理, 3-配置管理, 4-数据查看
    access = IntField(default=0)  # 1-普通， 2-城市， 3-集团， 4-超级
    username = StringField(default="")
    phone = StringField(default="")
    password = StringField(default="")
    password_num = IntField(default=0)
    area = ListField(default=[])
    area_str = StringField(default="")

    meta = {'collection': 'web_user'}

    @classmethod
    def check_area(cls, area, access):
        if access == 4: return True, [], '所有地区', ''
        d = {"1": "outer_project_id", "2": "outer_city_id", "3": "outer_property_id"}
        _d = {"1": "project", "2": "city", "3": "property_name"}
        area = list(set(area))
        area_str = []
        for outer_id in area:
            if not Basedata_Project.objects(__raw__={d[str(access)]: outer_id}):
                return False, None, "", "%s %s not exits" % (d[str(access)], outer_id)
            project_obj = Basedata_Project.objects(__raw__={d[str(access)]: outer_id}).first()
            area_str.append(getattr(project_obj, _d[str(access)]))
        return True, area, ",".join(area_str), ""

    @classmethod
    @method_set_rds(60)
    def get_access_project_info(cls, user_obj):
        if user_obj.access == 4:
            project_obj_list = Basedata_Project.objects(status="1")
        else:
            d = {"1": "outer_project_id", "2": "outer_city_id", "3": "outer_property_id"}
            project_obj_list = []
            for outer_id in user_obj.area:
                project_obj_list += Basedata_Project.objects(__raw__={d[str(user_obj.access)]: outer_id})
        return [project_obj.get_project_info() for project_obj in project_obj_list]

    def get_web_user_info(self):
        return {
            "id": str(self.id),
            "role_list": self.role_list,
            "access": self.access,
            "username": self.username,
            "phone": self.phone,
            "area": self.area,
            "area_str_list": self.area_str.split(","),
            "status": self.status,
        }

    @classmethod
    def get_web_user_by_phone(cls, phone):
        raw_query = {
            'phone': phone,
            'role_list': {'$all': [3]},
            'status': '1',
        }
        web_user = Web_User.objects(phone=phone).first()
        if web_user:
            return {
                'phone': web_user.phone,
            }
        return None
