# coding=utf8
import datetime
from mongoengine import *

from models.base import QdModelMixin


__doc__="""
系统中的帐户模型
"""


class AppDevice(QdModelMixin, Document):
    """手机设备信息"""
    meta = {"strict": False}
    user = ReferenceField('QdUser')

    manufacturer = StringField(default="")
    model = StringField(default="")
    build_id = StringField(default="")
    sdk = StringField(default="")
    rom = StringField(default="")


class QdUser(QdModelMixin, Document):
    """
    QD App User
    """

    # 外部数据来源， 以及基本的外部原数据
    source_data_info = DictField(default={})
    domain = StringField(default="sz.qdingnet.com")
    user_name = StringField(default="", unique=True)  # 用户名
    password = StringField(default="")  # 密码
    dpassword = StringField(default="")  # 动态密码

    gender = StringField(default="M")  # 姓别
    mobile = StringField(default="")  # 手机号
    identity_card = StringField(default="")  # 身份证
    real_name = StringField(default="")  # 真实姓名
    avatar = ReferenceField('ImageAppAvatar')

    last_login_at = DateTimeField(default=datetime.datetime.now)  # 最后登陆时间
    related_aptms = ListField(ReferenceField('Room'), default=[])  # 绑定的房间列表

    settings = DictField(default={

        # 与报警网关相关的通知选项
        "agw_notice": {"alarm": True, "delay_alarm": False, "bcf": False, "offline": True}
    })

    meta = {
        "strict": False,
        'index_background': True,
        "indexes": [
            "domain", "mobile", {"fields": ["source_data_info.outer_id"], "sparse": True}
        ]
    }


class WuyeUser(QdModelMixin, Document):
    """
    QD Wuye User
    """
    meta = {"strict": False}
    user_name = StringField(default="", unique=True)  # 用户名
    password = StringField(default="")  # 密码
    gender = StringField(default="M")  # 姓别
    last_login_at = DateTimeField(default=datetime.datetime.now)  # 最后登陆时间
    project = ReferenceField('Project')  # 管理的楼盘项目

class MgrUser(QdModelMixin, Document):
    """
    QD System Manager User
    """
    meta = {"strict": False}
    user_name = StringField(default="", unique=True)  # 用户名
    password = StringField(default="")  # 密码
    gender = StringField(default="M")  # 姓别
    last_login_at = DateTimeField(default=datetime.datetime.now)  # 最后登陆时间

