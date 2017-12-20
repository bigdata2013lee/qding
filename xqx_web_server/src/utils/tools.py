# coding=utf-8
import hashlib
import json
import logging
import pickle
import random
import threading
import uuid
import math
import re
import requests
import time
import datetime

from conf.qd_conf import CONF


log = logging.getLogger('django')


__doc__ == """
通用的工具包(小的，常用的工具方法)
注意:不要在头部直接import utils.qd, 因为它依赖了utils.tools
"""

comm_dev_partten = '^(10|11|12|13|20|21|22|23|30|31)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+)$'


def get_log(name=""):
    if not name:
        ft = '%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=ft)

    _log = logging.getLogger(name)
    return _log


def get_default_result():
    from utils import qd
    rs = qd.ResultDict(msg="", err=0, data={})
    return rs


def _compute_pagination(page_no, page_size, total_count, num_len=9):
    page_count = int(math.ceil(1.0 * total_count / page_size))
    page_count = 1 if page_count == 0 else page_count
    page_no = page_no if page_no < page_count else page_count
    start_no = page_no
    end_no = page_no

    while num_len > 1:
        if start_no > 1 and num_len > 0:
            start_no = start_no - 1
            num_len = num_len - 1
            if num_len == 0:
                break

        if end_no < page_count and num_len > 0:
            end_no = end_no + 1
            num_len = num_len - 1
            if num_len == 0:
                break

        if start_no == 1 and end_no == page_count:
            break

    pagination = {
        'page_no': page_no,
        'page_size': page_size,
        'page_count': page_count,
        'start_no': start_no,
        'end_no': end_no,
        'total_count': total_count,
        'has_pre': page_no > 1,
        'has_next': page_no < page_count
    }

    return pagination


def paginate_query_set(query_set, pager={}, **output_kwargs):
    """
    查询分页
    :param query_set:  查询对象结果集, 不是普通的列表.
    :param pager: {page_no:1, page_size:10}
    :param output_kwargs: pager后面的所有命名参数都传入 outputEx 方法
    :return:
    """
    page_no = pager.get("page_no", 1)
    page_size = pager.get("page_size", 10)

    cut = query_set[(page_no - 1) * page_size: page_no * page_size]
    cut_trans = [item.outputEx(**output_kwargs) for item in cut] if cut else []

    result = {
        "collection": cut_trans,
        "pagination": _compute_pagination(page_no, page_size, query_set.count())
    }
    return result


def md5_str(my_str=""):
    m = hashlib.md5()
    m.update(my_str.encode('utf-8'))
    return m.hexdigest()


def md5_bytes(my_bytes=b""):
    m = hashlib.md5()
    m.update(my_bytes)
    return m.hexdigest()


def get_uuid():
    return ("%s" % uuid.uuid4()).replace('-', '')


def set_dev_heartbeat_ex_timer(dev_type, dev_id, ex=90, net="Wi-Fi"):
    """在redis中记录设备心跳信息的统一入口方法"""
    from utils.qd import QdRds
    if dev_type == 'agw':
        ex = CONF['agw_heartbeat']['wifi_ex']
        if net != "Wi-Fi": ex = CONF['agw_heartbeat']['gsm_ex']

    heartbeat_rds = QdRds.get_heartbeat_redis()
    heartbeat_rds.set("%s_heartbeat_%s" % (dev_type, dev_id), int(time.time()), ex=ex)


def send_mobile_msg(mobile, content=""):
    url = "https://boss.qdingnet.com/qding-openapi/openapi/json/machine/smsRequest"
    params = "?body={'mobile':'%s','content':'%s'}" % (mobile, content)
    session = requests.Session()
    response = session.get(url + params)

    return True


def send_push_message(content="", extras={}, alias=[], tags=[], domains=['sz.qdingnet.com']):
    """
    发送极光消息推送
    :param content: T-string, 消息内容
    :param extras: T-dict, 自定义数据
    :param alias: T-list, 用户/设备ID 列表
    :param tags: T-list, 组 列表
    :return:

    :notice: 会把消息存入redis队列中，交给message_push进程处理
    """
    from utils.qd import QdRds
    _rds = QdRds.get_redis()

    if not domains: domains = ["sz.qdingnet.com"]

    if isinstance(domains, str): domains = [domains]
    domain_push_map = {"sz.qdingnet.com": "jpush", "www.qdingnet.com": "bj_push"}

    def __select_push(params_json):
        for domain in domains:
            _rds.lpush(domain_push_map.get(domain, "jpush"), params_json)

    if alias:
        if isinstance(alias, str): alias = [alias]
        _params_json = json.dumps(dict(content=content, extras=extras, alias=alias))
        __select_push(_params_json)

    if tags:
        if isinstance(tags, str): tags = [tags]
        _params_json = json.dumps(dict(content=content, extras=extras, tags=tags))
        __select_push(_params_json)


def match_device_cls_by_uuid(dev_uuid):
    """
    选择 设备 Model Class
    :param dev_uuid:
    :return: Model Class
    """

    from models.device import UnitGate, FenceGate, AioManager

    dev_info = parse_device_uuid(dev_uuid)

    if not dev_info: return None

    dev_type = int(dev_info[0])

    device_selector = {

        20: UnitGate,  # 单元门口机
        22: FenceGate,  # 围墙机
        30: AioManager,  # 管理机

    }

    _dev_model = device_selector.get(dev_type, None)
    return _dev_model


def get_device_by_uuid(dev_uuid):
    """
    通过设备UUID, 查询设备对象
    :param dev_uuid:
    :return:
    """
    dev_cls = match_device_cls_by_uuid(dev_uuid)
    if not dev_cls:
        log.warning("dev uuid [%s] 错误, 无法找到相应的数据模型类", dev_uuid)
        return None

    dev = dev_cls.objects(dev_uuid=dev_uuid).first()
    if not dev: return None

    return dev


def parse_device_uuid(dev_uuid):
    """
    解析 设备UUID, 返回各字段含义
    dev_type, phase, build, unit, floor, room, dev_no
    :param dev_uuid:
    :return:
    """
    find = re.findall(comm_dev_partten, dev_uuid)
    if not find: return None
    return [int(x) for x in find[0]]


def parse_apartment_fuuid(aptm_fuuid):
    """
    把带格式的房间编号转换为序列
    1-10-3-8-5 ->　[1,10,3,8,5]
    :param aptm_fuuid:
    :return: T-list

    """
    find = re.findall(r'^(\d+)-(\d+)-(\d+)-(\d+)-(\d+)$', aptm_fuuid)
    if not find: return None
    return [int(x) for x in find[0]]


def parse_apartment_uuid(aptm_uuid):
    """
    把不带格式的房间编号转换为序列
    001010003008005 ->　[1,10,3,8,5]
    :param aptm_uuid:
    :return: T-list
    """
    find = re.findall(r'^(\d{3})(\d{3})(\d{3})(\d{3})(\d{3})$', aptm_uuid)
    if not find: return None
    return [int(x) for x in find[0]]


def parse_aptm_codes_to_uuid(codes):
    """
    把序列转换为aptm_uuid
    [1,10,3,8,5] -> 001010003008005
    :param codes:
    :return:
    """
    return "{0:0>3}{1:0>3}{2:0>3}{3:0>3}{4:0>3}".format(*codes)


def parse_codes_to_aptm_uuid_pattern(codes):
    """
    把序列转为正则,通常用于房间UUID查询

    [1,2,3] -> "^001002003"
    [0,2,3] -> "^\d{3}20003"
    :param codes:
    :return:
    """
    return "^" + "".join(["{:0>3}".format(x) if x else "\d{3}" for x in codes])


def parse_aptm_short_code(aptm_short_code):
    """
    104 - > [1,4]
    :param aptm_short_code:
    :return:
    """
    find = re.findall('(\d{1,3})(\d{2})\s*$', aptm_short_code)
    short_codes = [0, 0]
    if find: short_codes = [int(x) for x in find[0]]

    return short_codes


def bytes_check_sum(data):
    """
    计算bytes的chksum
    :param data:
    :return: T-int
    """
    ck_num = 0
    for d in data:
        ck_num = ck_num + d
        ck_num = ck_num % 0x100

    ck_num = 0xff - ck_num

    return ck_num


def rds_api_cache(ex, think_session=True, mgr_key=""):
    """
    Api方法结果缓存， Api方法参数要求是简单的类型， 装饰器排列在最底层
    :param ex: T-int, 设置过期时间
    :param think_session: bool, 是否考虑session登陆的问题，如果查询中使用了登陆者信息，必须设置为True
    :param mgr_key: T-string, 管理键eval表达式
    :example:

    @xxx
    @rds_api_cache(ex=60)
    def api_method(self):
    """

    def wrapper(func):
        def _d(*args, **kwargs):

            from utils.qd import QdRds
            rds = QdRds.get_redis()

            def _mk_func_name_key():
                inst = args[0]

                find = re.findall("function\s+(.+)\s+at", "%s" % func)
                func_name = find[0]
                session_id = ""
                if think_session:
                    session_id = "%s" % inst.request.session.session_key if getattr(inst, "request", None) else ""

                _str_args = str(args[1:]) if len(args) > 1 else ""

                keys = ["%s" % k for k in kwargs.keys()]
                keys.sort()
                vals = []
                for k in keys: vals.append("%s" % kwargs.get(k, ""))

                # 注意 md5不能保证唯一，有可能出现错误的缓存值
                _params_key = md5_str("%s|%s=%s" % (_str_args, keys, vals))
                func_name_key = "api_cache_" + func_name
                _mgr_key = "[mgr_key-%s]" % eval(mgr_key) if mgr_key else ""
                func_key = func_name_key + _mgr_key + ":" + _params_key + ("|session:%s" % session_id if think_session else "")

                return func_key

            func_key = _mk_func_name_key()
            log.debug("rds_api_cache -> func_key:%s", func_key)
            dumps_data = rds.get(func_key)

            if dumps_data is None:
                rs = func(*args, **kwargs)
                dumps_data = pickle.dumps(rs)
                rds.set(func_key, dumps_data, ex=ex)

                return rs

            log.debug("rds_api_cache -> loads dumps_data")
            rs = pickle.loads(dumps_data)
            return rs

        return _d

    return wrapper


def synchronized(func):
    """
    synchronized 装饰器 像java一样修饰方法
    强调修饰小方法，不要用于大代码块
    """
    _lock = threading.Lock()

    def synced_func(*args, **kwargs):
        with _lock:
            return func(*args, **kwargs)

    return synced_func


def longlong_date():
    return datetime.datetime.strptime("2600/01/01 0:0:0", "%Y/%m/%d %H:%M:%S")


def decode_int(num):
    """
    把整数进行62进制压缩
    :param num:
    :return:
    """
    letters = "J0XljpKDQY8rE4OqtcoAbFex7aizf3C1k9GMwPTVZmvIWL6BYHNdsyS5nygh2R"
    jj = len(letters)
    indexs = []
    while True:
        if num < jj:
            indexs.append(num)
            break
        num, n = int(num / jj), int(num % jj)
        indexs.append(n)

    indexs.reverse()
    int_str = "".join([letters[x] for x in indexs])
    return int_str


def random_str(length=6, ignorecase=False):
    letters = "J0XljpKDQY8rE4OqtcoAbFex7aizf3C1k9GMwPTVZmvIWL6BYHNdsyS5nygh2R"
    mystr = "".join([random.choice(letters) for i in range(0, length)])
    if ignorecase: mystr = mystr.lower()
    return mystr


def mk_process_crt(log=None):
    import signal, os, sys
    if not log:
        log = logging.getLogger()
        log.level = 3

    crt = {"stop": False, "exit_code": 0}

    def process_exception_exit(fun):

        def _w(*args, **kwargs):
            res = None
            try:
                res = fun(*args, **kwargs)
            except Exception as e:
                log.warning("进程:%s 关键线程异常" % os.getpid())
                crt['stop'] = True
                crt['exit_code'] = 10
                log.exception(e)

            return res

        return _w

    def reg_signal_term(ext_fun=None):

        def onsignal_term(a, b):
            log.info("进程:%s, 接收到STOP[TERM]信号" % os.getpid())
            crt['stop'] = True

            if ext_fun:
                ext_fun()

        signal.signal(signal.SIGTERM, onsignal_term)

    def is_stop_status():
        return crt.get("stop")

    def process_exit_status():
        sys.exit(crt.get("exit_code"))

    return process_exception_exit, reg_signal_term, is_stop_status, process_exit_status


def match_file_name_suffix(file_name):
    """获取文件名后缀"""
    suffix = ""
    find = re.findall("(\.\w+)$", file_name)
    if find: suffix = find[0]
    return suffix
