# --*-- coding:utf8 --*--
from mongoengine.document import DynamicDocument
from apps.common.classes.Base_Class import Base_Class
from mongoengine.fields import StringField, FloatField, DictField


class User_Request(Base_Class, DynamicDocument):
    url = StringField(default="")
    error_result = DictField(default={})
    error_params = DictField(default={})
    request_time = FloatField(default=0.0)

    meta = {'collection': 'user_request'}

    @classmethod
    def get_request_by_filter(cls, order_filed='-created_field', **kargs):
        query = {}
        for k, v in kargs:
            if v:query.update({k:v})
        return User_Request.objects(**query).order_by(order_filed)

    @classmethod
    def get_request_day_count(cls, day):
        return User_Request.objects(created_time__gte=day).count()

    @classmethod
    def get_most_busy_url(cls, day):
        return

    def get_request_info(self):
        return {
            "url": self.url,
            "error_result": self.error_result,
            "error_params": self.error_params,
            "request_time": self.request_time,
        }
