# --*-- coding:utf8 --*--
import re
import time
import json


def validate_pagination(page_size, page_no):
    if not page_size:
        return True, ""
    page_size = str(page_size)
    page_no = str(page_no)
    page_pattern = re.compile('^[1-9][0-9]*$')
    if not page_pattern.match(page_size) or not page_pattern.match(page_no):
        return False, "page_no and page_size must be number  and  can not be 0"
    return True, ""


def validate_timestamp(timestamp_str, key_str, num=9):
    if not timestamp_str: return False, "%s can not be empty" % key_str
    pat_str = '^[1-9][0-9]{%s}$' % num
    pattern = re.compile(pat_str)
    if not pattern.match(str(timestamp_str)):
        return False, "%s must be 10 digits" % key_str
    return True, ""


def validate_filename(filename):
    if not filename:
        return False, "文件名不能为空"
    filename = str(filename)
    filename_re = re.compile("^[a-zA-Z][a-zA-Z_0-9\.]+[a-zA-Z]$")
    if not filename_re.match(filename):
        return False, "文件名格式为xxx.xxx.xxx"
    return True, ""


def validate_mac(mac):
    if not mac:
        return False, "mac can not be empty"
    mac_re = re.compile("^\s*([0-9a-fA-F]{2,2}[:|-]*){5,5}[0-9a-fA-F]{2,2}\s*$")
    if not mac_re.match(mac):
        return False, "mac should like 112233445566"
    return True, ""


def validate_contain_chinese_str(str_name, str_value, start_pos=1, end_pos=20):
    if not str_value: return False, "%s can not emtpy" % str_name
    str_re = re.compile('^[u4e00-u9fa5\w]{%s,%s}$' % (start_pos, end_pos))
    if not str_re.match(str_value):
        return False, "%s must be %s-%s character，include chinese" % (str_name, start_pos, end_pos)
    return True, ""


def validate_str(str_name, str_value, start_pos=1, end_pos=20):
    if not str_value: return False, "%s can not emtpy" % str_name
    str_re = re.compile('^\w{%s,%s}$' % (start_pos, end_pos))
    if not str_re.match(str(str_value)):
        return False, "%s must be %s-%s character，include chinese" % (str_name, start_pos, end_pos)
    return True, ""


def validate_gender(gender):
    if gender not in ['M', 'F']:
        return False, "性别必须M或者F"
    return True, ""


def validate_phone(phone):
    if not phone:
        return False, "手机号不能为空"
    phone = str(phone)
    phone_re = re.compile("^1\d{10}$")
    if not phone_re.match(phone):
        return False, "手机号必须是11位数字"
    return True, ""


def validate_phone_list(phone_list):
    if not phone_list:
        return False, "phone_list can not be empty"
    if not isinstance(phone_list, list):
        return False, "phone_list can only be list"
    for phone in phone_list:
        phone_flag, phone_str = validate_phone(phone)
        if not phone_flag: return phone_flag, phone_str
    return True, ""


def validate_email(email):
    email_re = re.compile("^[0-9a-zA-Z_\.#]+@(([0-9a-zA-Z]+)[.])+[a-z]{2,4}$")
    if not email_re.match(email):
        return False, "please input illegal email"
    return True, ""


def validate_num(num, num_str):
    num_re = re.compile("^\d+$")
    if not num_re.match(num):
        return False, "%s必须是数字" % num_str
    return True, ""


def validate_mongodb_id(mongodb_id):
    if not mongodb_id:
        return False, "db id can not be empty"
    mongodb_id = str(mongodb_id)
    mongodb_id_re = re.compile("^[0-9a-f]{24}$")
    if not mongodb_id_re.match(mongodb_id):
        return False, "mongodb id can only 24 digits"
    return True, ""


def validate_no(no, key_str, start=1, end=10):
    no_re = re.compile("^\d{%s,%s}$" % (start, end))
    if not no_re.match(str(no)):
        return False, '%s should be %s-%s length digits' % (key_str, start, end)
    return True, ''


def validate_clear_list(clear_list):
    if not clear_list:
        return False, "clear_list must can not be empty"
    if not isinstance(clear_list, list):
        return False, "clear_list must be a list"
    if len(clear_list) > 10:
        return False, "the length of clear_list must within 10"
    return True, ""
