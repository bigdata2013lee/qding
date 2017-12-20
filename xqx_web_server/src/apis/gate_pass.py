# coding=utf-8
import datetime
import logging
from collections import namedtuple
from apis.base import BaseApi
from models.aptm import Room
import random
import re

from utils import tools
from utils.permission import app_user_login_required, common_login_required
from utils.qd import DistributedLock, QdRds
from utils.tools import get_default_result, rds_api_cache

log = logging.getLogger('django')

six_password_black_list = [
    111111, 222222, 333333, 444444, 555555, 666666, 777777, 888888, 999999,
    123456, 654321, 456789, 987654, 147258, 258369, 963852, 963258, 258147, 258741,
    789456, 789654, 456123, 456321, 111222, 222333, 333444, 444555, 555666, 666777, 888999
]

PWD = namedtuple("PWD", "ptype,password,project_id,date_str,aptm_id,user_id")


def get_now_date_str():
    """
    当天日期 return->20160408
    """
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d")


def get_ex_val():
    """
    计算当前时间至24:00的时间差(秒)
    """
    now = datetime.datetime.now()
    end_date = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
    return int(end_date.timestamp() - now.timestamp()) + 1


class GatePasswordPassApi(BaseApi):
    """
    用户获取开门密码，门口机验证开门密码，生成密码池
    """

    @common_login_required
    def validate_user_password(self, password):
        """
        门口机验证用户通行密码(6位)
        :param password: T-string, 密码
        :return: data->{"enable": #Bool}
        """
        from apis.gate import GateApi

        result = get_default_result()
        gate = self._get_login_device()
        day_str = get_now_date_str()

        if not password or not re.findall("^\d{6}$", password):
            return result.setdata('enable', False)

        rds = QdRds.get_redis()

        password_search_key = "*_pass_pwd:%s,%s,%s,*,*" % (password, gate.project.id, day_str)
        password_keys = [key.decode('utf-8') for key in rds.keys(password_search_key)]

        log.debug("password_keys:%s", password_keys)

        if not password_keys:
            return result.setdata('enable', False)

        password_key = password_keys[0]
        pwd_val = rds.get(password_key).decode('utf-8')
        find = re.findall("\w+", password_key)
        pwdK = PWD._make(find)

        log.debug("pwdK:%s", pwdK)

        if not self._check_open_gate(pwdK.aptm_id, gate):
            return result.setdata('enable', False)

        # 一次密码，此门已通过
        if pwdK.ptype == 'once_pass_pwd' and str(gate.id) in pwd_val:
            return result.setdata('enable', False)

        # 一次密码，此门未曾通过
        elif pwdK.ptype == 'once_pass_pwd':
            pwd_val += ",%s" % gate.id
            rds.set(password_key, pwd_val)

        # 多次密码
        elif pwdK.ptype == "intraday_pass_pwd":
            pass

        opener_infos = {"pwd": pwdK.password, "user_id": pwdK.user_id, "aptm_id": pwdK.aptm_id}

        GateApi()._set_request(self.request)\
            .report_open_lock(open_way="resident_pwd", opener_infos=opener_infos)

        log.debug("%s:%s for user:%s", pwdK.ptype, pwdK.password, pwdK.user_id)

        return result.setdata('enable', True)

    @app_user_login_required
    def user_get_intraday_password(self, aptm_id):
        """
        App用户获取当天有效密码
        :param aptm_id: T-string, 房间ID
        :return: data->{"password": "123456"}
        """
        result = get_default_result()
        user = self._get_login_user()
        room = Room.objects(id=aptm_id).first()
        if not room: return result.setmsg("房间不存在", 3)

        rds = QdRds.get_redis()
        day_str = get_now_date_str()
        password_search_key = "intraday_pass_pwd:*,*,%s,%s,%s" % (day_str, room.id, user.id)
        password_keys = [key.decode("utf-8") for key in rds.keys(password_search_key)]

        # 如果密码已经存在，把它返回给APP
        if password_keys:
            pwdK = PWD._make(re.findall('\w+', password_keys[0]))
            return result.setdata('password', pwdK.password)

        password = self._get_password_from_pool(room.project.id, day_str)

        if not password:
            return result.setmsg("获取密码失败", 3)

        password_key = "intraday_pass_pwd:%s,%s,%s,%s,%s" % (password, room.project.id, day_str, room.id, user.id)
        rds.set(password_key, password, ex=get_ex_val())

        result.data['password'] = password
        return result

    @app_user_login_required
    @rds_api_cache(ex=60, think_session=True)
    def user_get_once_password(self, aptm_id):
        """
        App用户获取一次有效密码(同样是当天内有效)
        1.如果密码当天通过了A门，则当天不能再次通过A门
        2.一个用户一个房间，当天最多可申请10次

        :param aptm_id: T-string, 房间ID
        :return: data->{"password": "123456", times:#int->次数}
        """
        result = get_default_result()
        user = self._get_login_user()
        room = Room.objects(id=aptm_id).first()
        if not room: return result.setmsg("房间不存在", 3)

        rds = QdRds.get_redis()
        day_str = get_now_date_str()
        password_search_key = "once_pass_pwd:*,*,%s,%s,%s" % (day_str, room.id, user.id)
        password_keys = [key.decode("utf-8") for key in rds.keys(password_search_key)]

        if password_keys and len(password_keys) >= 10:
            return result.setmsg("获取访客密码超过10次", 3)

        password = self._get_password_from_pool(room.project.id, day_str)
        if not password:
            return result.setmsg("获取密码失败", 3)

        password_key = "once_pass_pwd:%s,%s,%s,%s,%s" % (password, room.project.id, day_str, room.id, user.id)
        rds.set(password_key, "", ex=get_ex_val())  # 第二个参数为空， 此处将会放入已通行的门口机ID

        result.data = dict(password=password, times=len(password_keys) + 1)
        return result

    def _get_password_from_pool(self, project_id, day_str):
        """
        从密码池中取出一个密码，
        如果密码池不存在，则创建它
        :param project_id:
        :param day_str:
        :return:
        """
        pool_key = "password_pool:%s_%s" % (project_id, day_str)
        rds = QdRds.get_redis()

        if not rds.exists(pool_key):
            with DistributedLock(pool_key, timeout=2, ex=2):  # 分布式锁
                self._created_password_pool(pool_key)

        password = rds.spop(pool_key)
        return (password or b'').decode("utf-8")

    def _created_password_pool(self, pool_key, pool_size=20000):
        """
        为项目当天创建2W长度的密码池
        :notice: pool_key 中包涵了project,date信息
        """
        rds = QdRds.get_redis()
        if rds.exists(pool_key): return

        bl = six_password_black_list
        pool = []

        while len(pool) < pool_size:
            for x in range(5000): pool.append(random.randint(100, 999999))
            pool = list(set(pool) - set(bl))[0:pool_size]

        pool = ["{:0>6}".format(n) for n in pool]

        rds.sadd(pool_key, *pool)
        rds.expire(pool_key, get_ex_val())

    def _check_open_gate(self, room_id, gate):
        """检测一个房间能否通过一个门"""

        room = Room.objects(id=room_id).first()
        if not room: return False

        dev_uuid = gate.dev_uuid
        dev_locs = tools.parse_device_uuid(dev_uuid)[1:4]
        aptm_uuid = room.aptm_uuid

        p = "^" + "".join(["\d{3}" if x == 0 else "{:0>3}".format(x) for x in dev_locs])
        return True if re.findall(p, aptm_uuid) else False
