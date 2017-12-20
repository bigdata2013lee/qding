# coding=utf8
import datetime
from mongoengine import *

from models.base import QdModelMixin


__doc__="""
系统中的帐户模型
"""


class MgrUser(QdModelMixin, Document):
    """
    QD System Manager User
    """
    meta = {"strict": False}
    user_name = StringField(default="", unique=True)  # 用户名
    password = StringField(default="")  # 密码
    gender = StringField(default="M")  # 姓别
    last_login_at = DateTimeField(default=datetime.datetime.now)  # 最后登陆时间


class AppUser(QdModelMixin, Document):
    """
    App User
    """
    meta = {"strict": False}
    phone = StringField(default="", unique=True)
    password = StringField(default="")
