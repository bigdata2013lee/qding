# -*- coding: utf-8 -*-
import json
import os
import re
import random
import multiprocessing
import traceback
import logging
logger = logging.getLogger('qding')


def convert(ch):
    try:
        length = len('柯')
        intord = ord(ch[0:1])
        if (intord >= 48 and intord <= 57):
            return ch[0:1]
        if (intord >= 65 and intord <= 90) or (intord >= 97 and intord <= 122):
            return ch[0:1].lower()
        ch = ch[0:length]  # 多个汉字只获取第一个
        with open(os.path.split(os.path.realpath(__file__))[0] + os.sep + r'convert-utf-8.txt') as f:
            for line in f:
                if ch in line:
                    return line[length:length + 1].upper()
    except:
        return ""


def is_digit(value):
    try:
        float(value)
    except:
        return False
    else:
        return True


def isValidIp(ip):
    if re.match(r"^\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*$", ip): return True
    return False


def isValidMac(mac):
    if re.match(r"^\s*([0-9a-fA-F]{2,2}[:|-]){5,5}[0-9a-fA-F]{2,2}\s*$", mac): return True
    return False


def isValidEmail(email):
    if re.match(r"^[0-9a-zA-Z_\.#]+@(([0-9a-zA-Z]+)[.])+[a-z]{2,4}$", email): return True
    return False


def isValidPhone(phone):
    if re.match(r"^\d{11}$", phone): return True
    return False


def read_file(file_name, chunk_size=512):
    with open(file_name, "rb") as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def write_file(file_name, content):
    fp = open(file_name, 'wb')
    for chunk in content.chunks():
        fp.write(chunk)
    fp.close()


def create_random_num(length):
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    x = [random.choice(chars) for i in range(length)]
    random_num = "".join(x)
    return random_num


def add_update_process(process_name, process_dict, rc):
    value = json.dumps({process_name: process_dict})
    return rc.sadd('update_process', value)


def start_process(target, args=()):
    try:
        p = multiprocessing.Process(target=target, args=())
        p.daemon = False
        p.start()
    except Exception as e:
        logging.exception(e)
        logging.exception(traceback.format_exc())


def get_key_from_dict(kargs):
    redis_key = "dump_brake_machine_data"
    keys = list(kargs.keys())
    keys.sort()
    for k in keys:
        redis_key = "%s%s%s" % (redis_key, k, kargs[k])
    return redis_key


def get_index_from_dict_list(k, v, f_list):
    for i in range(len(f_list)):
        if f_list[i][k] == v: return i
    return -1