# -*- coding: utf-8 -*-

from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField, DictField, IntField, DateTimeField
from apps.brake.api.Pass_Data_Init_Processor import Pass_Data_Init_Processor
from apps.brake.api.Pass_Data_Status_Processor import Pass_Data_Status_Processor
from apps.brake.api.Pass_Data_Sync_Processor import Pass_Data_Sync_Processor
from apps.common.utils.sentry_date import get_datetime_by_timestamp, get_str_time_by_timestamp, get_timestamp_by_str_day
from apps.common.utils.redis_client import rc
from apps.common.utils.qd_decorator import method_set_rds


class Brake_Open_Time(Base_Class, DynamicDocument):
    outer_app_user_id = StringField()
    machine_mac = StringField()
    pass_info = DictField(default={
        "pass_type": "0", #0-bluetooth, 1-WiFi
        "pass_mode": 100, #100-手动,101-无障碍通行
        "pass_time": None,
        "pass_result_code": None,
    })
    pass_time_cost = DictField()
    app_device_info = DictField(default={
        "device_model": "",
        "app_version": "",
        "platform": "",
        "platform_version": "",
    })

    meta = {"collection": "brake_open_time"}
