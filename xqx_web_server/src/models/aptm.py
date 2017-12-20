#coding=utf-8
import datetime
import re
import threading
from mongoengine import *

from models.account import QdUser
from models.base import QdModelMixin
from utils import tools

thread_local = threading.local()

class PCity(Document):
    """
    省 document
    """
    id = StringField(primary_key=True)
    name = StringField(default="")
    is_valid = BooleanField(default=False)
    order_num = IntField(default=0)     # 排序
    childs = ListField(default=[])      # 市列表

    meta = {"strict": False}

    @classmethod
    def get_pcity(cls, pid):
        """
        获取省市信息
        :param pid: T-string, 省ID
        :return:
        """
        pcity = cls.objects(id="%s" % pid).first()
        if pcity:
            return pcity.to_mongo()

        return None

    @classmethod
    def get_ccity(cls, cid, project={}):
        """
        获取城市信息
        :param cid: T-string, 城市ID
        :param project: T-obj, 自定义输出
        :return:
        """

        pipelines = [
            {"$match": {"childs._id": "%s" % cid}},
            {"$unwind": "$childs"},
            {"$match": {"childs._id": "%s" % cid}},
            {"$project": project or {"pname": "$name", "cname": "$childs.name", "id": "$childs._id", "pid": "$_id", "_id": 0}}
        ]
        cursor = PCity.objects().aggregate(*pipelines)

        for city in cursor:
            return city

        cursor.close()

        return None

class Project(QdModelMixin, Document):

    # 外部数据来源， 以及基本的外部原数据
    source_data_info = DictField(default={})
    domain = StringField(default="sz.qdingnet.com")
    ccity_id = StringField(default="")
    code = StringField(default="00000001", unique=True) # 7-8位数字项目编号，便于在门口机中输入
    street = StringField(default="")
    label = StringField(default="")
    meta = {"strict": False}


class Room(QdModelMixin, Document):

    # 外部数据来源， 以及基本的外部原数据
    source_data_info = DictField(default={})

    domain = StringField(default="sz.qdingnet.com")

    project = ReferenceField("Project")  # 项目
    aptm_uuid = StringField(default="000" * 5)  # 房间UUID etc: 001002003004005
    pre_names = DictField(default=dict(phase="", building="", unit=""))

    residents = ListField(ReferenceField('QdUser'), default=[])  # 住户列表
    master = ReferenceField('QdUser')  # 住户管理员
    talk_contact_phone = StringField(default="")  # 对讲转接电话

    meta = {
        "strict": False,
        'index_background': True,
        "indexes": [
            "domain", "project", "aptm_uuid", "$aptm_uuid",
            {"fields": ["source_data_info.outer_id"], "sparse": True}
        ]
    }

    def get_aptm_pre_names(self):
        """
        计算出房间的两个前缀名
        ("a小区b期c栋", "b期c栋")
        为减少对项目，期，栋数据在短时间内的多少查询，把结果缓存到ThreadLocal中
        :return:
        """
        if not getattr(thread_local, "project_names_cache", None):
            thread_local.project_names_cache = {}

        project_id = "%s" % self.project.id if self.project else ""
        project_name = thread_local.project_names_cache.get("project:%s" % project_id, None)
        if not project_name:
            project_name = self.project.name or ""
            thread_local.project_names_cache[project_id] = project_name

        pre_names = (project_name, self.pre_names.get("phase", ""), self.pre_names.get("building", ""))

        return pre_names

    def get_aptm_full_name(self):
        return "".join(self.get_aptm_pre_names()) + self.name

    def get_aptm_short_name(self):
        return "".join(self.get_aptm_pre_names()[1:]) + self.name

    def get_locs(self, fmt="dict"):

        _names = ['phase', 'building', 'unit', 'floor', 'room']

        fmt_list = tools.parse_apartment_uuid(self.aptm_uuid)
        fmt_dict = dict(zip(_names, fmt_list))

        if not fmt or fmt == 'dict': return fmt_dict
        return fmt_list

    def rebuild_aptm_name(self, save=False):
        self.name = "{0[unit]}单元{0[floor]}{0[room]:0>2}室".format(self.get_locs())
        if save: self.saveEx()

    def outputEx(self, inculde_fields=[], exculde_fields=["source_data_info"], ex_fun=None):
        obj = self.to_python(inculde_fields=inculde_fields, exculde_fields=exculde_fields)
        obj["pre_names"] = self.get_aptm_pre_names()
        obj['aptm_locs'] = self.get_locs("dict")
        if ex_fun: ex_fun(self, obj)
        return obj

    def order_residents(self, order_residents=[]):
        """
        调整住房列表顺序
        :param order_residents: T-[#str,...]
        :return:
        """
        residents = self.residents
        if not order_residents or not residents: return
        order_map = {}
        order_num = 1
        for or1 in order_residents:
            order_map[or1] = order_num
            order_num += 1

        def _cmp_key(o):
            return order_map.get("%s" % o.id, 100000)

        residents.sort(key=_cmp_key)
        self.residents = residents
        self.saveEx()
