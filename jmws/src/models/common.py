# coding=utf-8
import datetime
from mongoengine import *
from models.base import QdModelMixin




class Sysconfig(Document):
    """系统配置参数"""
    name = StringField(unique=True)  # 参数名称/key
    options = DictField(default={})  # 参数选项




