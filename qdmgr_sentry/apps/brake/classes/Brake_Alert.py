# -*- coding:utf-8 -*-
from bson.objectid import ObjectId
from apps.common.classes.Base_Class import Base_Class
from mongoengine.document import DynamicDocument
from mongoengine.fields import ReferenceField, StringField
from apps.web.classes.Web_User import Web_User


class Brake_Alert(Base_Class, DynamicDocument):
    alert_email = StringField(default="")
    web_user = ReferenceField(Web_User, default=None)
    meta = {'collection': 'brake_alert'}

    def get_alert_by_user(self):
        return Brake_Alert.objects(web_user=self.web_user)

    def get_alert_info(self):
        return {
            "id": str(self.id),
            "alert_email": self.alert_email,
        }

    def get_alert_by_filter(self):
        raw_query = {}
        if self.web_user:
            raw_query.update({
                "web_user": ObjectId(self.web_user.id)
            })
        if self.alert_email:
            raw_query.update(
                {
                    "alert_email": self.alert_email
                }
            )
        return Brake_Alert.objects(__raw__=raw_query)

    def get_alert_by_id(self):
        return Brake_Alert.objects(id=self.id).first()
