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

import functools
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


def get_log(name="", level=10):
    if not name:
        ft = '%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] %(message)s'
        logging.basicConfig(level=level, format=ft)

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
    response = session.get(url + params, timeout=10)

    return True


def send_push_message(content="", extras={}, alias=[], tags=[], domains=['sz.qdingnet.com']):
    """
    发送消息推送
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
    domain_push_map = {"sz.qdingnet.com": "jpush",
                       "www.qdingnet.com": "bj_push"}

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


def convert_to_builtin_type(obj):
    """
    其它类型的对象转换为json str
    """
    from bson import ObjectId
    from mongoengine import Document
    import datetime

    if isinstance(obj, ObjectId):
        return "%s" % obj

    elif isinstance(obj, datetime.datetime):
        return "%.3f" % obj.timestamp()

    elif isinstance(obj, Document):
        return "%s" % obj.id

    raise Exception("%s is not JSON serializable" % obj)


def rds_api_cache(ex=60, think_session=True, mgr_key=""):
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

        @functools.wraps(func)
        def _d(*args, **kwargs):

            from utils.qd import QdRds
            rds = QdRds.get_redis()

            def _get_params_key():
                _args = args[1:]
                _kwargs = {}
                _kwargs.update(kwargs)

                for index, _arg in enumerate(_args):
                    _kwargs["_arg_%d" % index] = _arg

                pkey_name = json.dumps(_kwargs, sort_keys=True, default=convert_to_builtin_type)

                pkey = hashlib.sha256(pkey_name.encode("utf-8")).hexdigest()
                return pkey

            def _mk_func_name_key():
                inst = args[0]

                find = re.findall("function\s(\w+\.\w+)", "%s" % func)
                func_name = find[0]
                session_id = ""
                if think_session:
                    session_id = "%s" % inst.request.session.session_key if getattr(inst, "request", None) else ""

                _params_key = _get_params_key()

                func_name_key = "api_cache_" + func_name
                _mgr_key = "[mgr_key-%s]" % eval(mgr_key, {"args":args, "kwargs":kwargs}) if mgr_key else ""
                _func_key = func_name_key + _mgr_key + ":" + _params_key + ("|session:%s" % session_id if think_session else "")

                return _func_key

            func_key = _mk_func_name_key()
            log.debug("rds_api_cache -> %s", func_key)
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


def rpc_disable(func):
    """设置一个标记，标记此方法被remote_view通过Json Rpc方式调用"""
    func._rpc_disable = True
    return func


def longlong_date():
    return datetime.datetime.strptime("2600/01/01 0:0:0", "%Y/%m/%d %H:%M:%S")


def valiate_date(date_str):
    if not date_str: return False
    exp = "((^((1[8-9]\d{2})|([2-9]\d{3}))([\/])(10|12|0?[13578])([\/])(3[01]|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|([2-9]\d{3}))([\/])(11|0?[469])([\/])(30|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|([2-9]\d{3}))([\/])(0?2)([\/])(2[0-8]|1[0-9]|0?[1-9])$)|(^([2468][048]00)([\/])(0?2)([\/])(29)$)|(^([3579][26]00)([\/])(0?2)([\/])(29)$)|(^([1][89][0][48])([\/])(0?2)([\/])(29)$)|(^([2-9][0-9][0][48])([\/])(0?2)([\/])(29)$)|(^([1][89][2468][048])([\/])(0?2)([\/])(29)$)|(^([2-9][0-9][2468][048])([\/])(0?2)([\/])(29)$)|(^([1][89][13579][26])([\/])(0?2)([\/])(29)$)|(^([2-9][0-9][13579][26])([\/])(0?2)([\/])(29)$))"
    find = re.findall(exp, date_str)
    if find: return True
    return False

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


def match_file_name_suffix(file_name):
    """获取文件名后缀"""
    suffix = ""
    find = re.findall("(\.\w+)$", file_name)
    if find: suffix = find[0]
    return suffix






def run_task_threads(task_fun, thead_count=2, depend_ths=[]):
    """
    多线程执行某个任务
    :param task_fun:
    :param thead_count:
    :param depend_ths:
    :return:
    """
    threads = []

    for th in depend_ths:
        threads.append(th)
        th.start()

    for num in range(0, thead_count):
        t = threading.Thread(target=task_fun)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

