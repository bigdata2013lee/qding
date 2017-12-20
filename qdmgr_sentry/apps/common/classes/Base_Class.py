# -*- coding: utf-8 -*-

from mongoengine.fields import StringField, DateTimeField
from datetime import datetime


class Base_Class():
    status = StringField(default="1") #'1'=启用 '2'=禁用
    created_time = DateTimeField(default=datetime.now)
    updated_time = DateTimeField(default=datetime.now)

    def to_qd_json(self, fields_dic={}):
        qd_json = {}
        for k, v in fields_dic.items():
            inner_v = getattr(self, k)
            if isinstance(v, dict):
                try:
                    qd_json[k] = inner_v.to_qd_json(v)
                except:
                    qd_json[k] = v
                continue
            elif isinstance(inner_v, datetime):
                qd_json[k] = int(1000 * inner_v.timestamp())
                continue
            elif isinstance(inner_v, list):
                qd_json[k] = []
                if inner_v:
                    for vv in inner_v:
                        if isinstance(vv, Base_Class):
                            qd_json[k].append(vv.to_qd_json(v[0]))
                        else:
                            qd_json[k].append(v)
                continue
            elif inner_v:
                qd_json[k] = str(inner_v)
            else:
                qd_json[k] = ""
        return qd_json

    def get_have_value_fields(self, del_fields_list=["status", "created_time", "updated_time"]):
        fields_dic = self._db_field_map
        return [k for k in fields_dic.keys() if getattr(self, k) is not None and k not in del_fields_list]
