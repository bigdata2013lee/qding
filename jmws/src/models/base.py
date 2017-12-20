#coding=utf8
import datetime
import logging

from mongoengine import *

from conf.qd_conf import CONF
log = logging.getLogger('django')
connect(**CONF.get('mongo'))


class QdModelMixin(object):
    """ 全局 Model 依赖
        对 mongoengine-Document等作扩展支持.
    """
    is_valid = BooleanField(default=True)        # 数据是否有效, 默认为有效, 除非主动标记无效.(对数据只进行逻辑删除,而非物理删除)
    name = StringField(default="")              # 通用描述说明字段

    created_at = DateTimeField(default=datetime.datetime.now)     # 创建时间
    updated_at = DateTimeField(default=datetime.datetime.now)     # 更新时间

    def set_attrs(self, **kwargs):

        for k, v in kwargs.items(): setattr(self, k, v)
        return self

    def saveEx(self):
        """
        扩展 标准的 save()方法:
             - 支持每次 save()时, 自动更新 updated_at 字段
        """
        self.updated_at = datetime.datetime.now()
        _op = self.save()

        return _op

    def deleteEx(self):
        """ 逻辑删除, 标记数据为无效值
        :return:
        """
        self.is_valid = False
        self.saveEx()  # 标记无效, 并保存

    def outputEx(self, inculde_fields=[], exculde_fields=["source_data_info", "password","dpassword"], ex_fun=None):
        """
        标准输出, 子类可以根据需要,覆写之
        :return: 返回所有字段信息, type = dict
        """
        o = self.to_python(inculde_fields=inculde_fields, exculde_fields=exculde_fields)
        if ex_fun: ex_fun(self, o)
        return o

    @classmethod
    def is_exist_obj(cls, *args, **kwargs):
        obj = cls.objects(*args, **kwargs).first()
        if not obj: return False
        return True

    def to_python(self, inculde_fields=[], exculde_fields=[]):
        from bson import ObjectId
        son = self.to_mongo().copy()
        obj = {}
        fields = son.keys()

        if inculde_fields: fields = inculde_fields

        for field in exculde_fields:
            if field in fields: fields.remove(field)

        def _(target, key, v):
            if isinstance(v, ObjectId):
                target[key] = "%s" % v

            elif isinstance(v, datetime.datetime):
                #target[key] = int((v.timestamp() * 1000) - (8 * 3600 * 1000))
                target[key] = int(v.timestamp() * 1000)
            elif isinstance(v, dict) or isinstance(v, list):
                _fix(v)

        def _fix(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    _(o, k, v)

            elif isinstance(o, list):
                index = -1
                for v in o:
                    index += 1
                    _(o, index, v)

        for field_name in fields:
            _fn = field_name
            if field_name == '_id': _fn = 'id'
            val = son.get(field_name)
            obj[_fn] = val

        _fix(obj)
        return obj


