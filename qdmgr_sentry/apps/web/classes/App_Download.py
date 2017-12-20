# -*- coding: utf-8 -*-
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import StringField


class App_Download(DynamicDocument, Base_Class):
    agent = StringField(default="")

    meta = {'collection': 'app_download'}
