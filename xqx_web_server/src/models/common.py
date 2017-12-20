# coding=utf-8
import datetime
from mongoengine import *
from models.base import QdModelMixin
from utils import tools



class QDVersion(QdModelMixin, Document):
    """
    版本
    """
    version = StringField(default="")
    version_code = StringField(default="000000000")
    md5sum = StringField(default="")
    component_type = StringField(default="")
    component_desc = DictField(default={})
    filename = StringField(default="")
    bin_file = FileField(collection_name='upgrade')

    release_at = DateTimeField(default=datetime.datetime.now)  # 发布生效时间
    release_status = StringField(default="releaseing")  # 可选值 history-历史， releaseing-发布中， release_wait-等待发布中

    @classmethod
    def get_newest_version(cls, component_type):
        return QDVersion.objects(component_type=component_type, release_status="releaseing")\
            .order_by("-version_code").first()

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
                "component_type", "release_status"
        ]
    }



class AccessCard(QdModelMixin, Document):
    """
    门禁卡
    """
    TYPE_CHOICES = (('resident', '业主卡'), ('manager', '物业卡'), ('worker', '工作卡'))
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField("Project")

    card_no = StringField(required=True)  # 卡片编号
    card_type = StringField(choices=TYPE_CHOICES)  # 卡片类型
    owner_name = StringField(default="")  # 使用人名称
    expiry_date = DateTimeField(default=tools.longlong_date())  # 默认超长时间,有效期

    aptm_uuid = StringField(default="")  # 房号, 业主卡可访问此属性

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project", "card_type"
        ]
    }


class AptmApplication(QdModelMixin, Document):
    """
    房屋绑定申请
    """
    domain = StringField(default="sz.qdingnet.com")
    project = ReferenceField("Project")

    user = ReferenceField('QdUser')
    user_mobile = StringField(default="")
    user_realname = StringField(default="")

    target_aptm = ReferenceField("Room")
    target_aptm_name = StringField(default="")

    status = StringField(default="new")  # new|reject|pass

    wy_notice = StringField(default="")  # 物业备注

    user_type = StringField(default="住户")  # 申请者身份
    user_notice = StringField(default="")  # 用户备注

    meta = {
        "strict": False, 'index_background': True,
        "indexes": [
            "domain", "project"
        ]
    }

class ImageAppAvatar(QdModelMixin, Document):
    """
    App用户头像
    """
    meta = {"strict": False}
    ftype = StringField(default="jpg")
    fsize = IntField(default=0)
    base64 = StringField(default="")

class ImageCallSnapshot(QdModelMixin, Document):
    meta = {"strict": False}
    btype = StringField(default="index")

    ftype = StringField(default="jpg")
    fsize = IntField(default=0)
    base64 = StringField(default="")

    project = ReferenceField("Project")


class AdvMedia(QdModelMixin, Document):
    meta = {"strict": False}
    weight = IntField(default=1)
    adv_type = StringField(default="")
    company_name = StringField(default="")

    start_at = DateTimeField()
    end_at = DateTimeField()

    projects = ListField(ReferenceField('Project'), default=[])
    media_file = FileField(collection_name='advfs')
