# --*-- coding:utf8 --*--
import re
from conf.qd_conf import CONF


def validate_component_type(component_type):
    if not component_type:
        return False, "component_type can not be empty"
    return True, ""


def validate_mongodb_id(mongodb_id, id_str):
    if not mongodb_id:
        return False, "%s 不能为空" % id_str
    project_id_re = re.compile("[\da-f]{24}")
    if not project_id_re.match(mongodb_id):
        return False, "%s 只能是24位16进制数" % id_str
    return True, ""


def validate_version_json_file(version_json_file):
    if not version_json_file: return False, "亲，json文件内容不能为空"

    if not isinstance(version_json_file, dict): return False, "亲，json文件内容只能是字典"

    if version_json_file.keys() != set(["version", "md5sum", "component_type", "package_name", "component_desc"]):
        return False, "亲，json字典只能包含version, md5sum, component_type, component_desc, package_name五个key"

    version_flag, version_str = validate_version(version_json_file['version'])
    if not version_flag:
        return version_flag, version_str

    md5sum_flag, md5sum_str = validate_md5sum(version_json_file['md5sum'])
    if not md5sum_flag:
        return md5sum_flag, md5sum_str

    component_type_flag, component_type_str = validate_component_type(version_json_file['component_type'])
    if not component_type_flag:
        return component_type_flag, component_type_str

    component_desc_flag, component_desc_str = validate_component_desc(version_json_file['component_desc'])
    if not component_desc_flag:
        return component_desc_flag, component_desc_str

    return True, ""


def validate_version(version):
    if not version:
        return False, "亲，version值不能为空"
    version = str(version)
    version_re = re.compile("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}")
    if not version_re.match(version):
        return False, "亲，version格式不正确,请模仿这个1.1.1,注意各数字位不能超过三位数"
    return True, ""


def validate_component_type(component_type):
    if not component_type:
        return False, "亲，component_type值不能为空"

    return True, ""


def validate_md5sum(md5sum):
    if not md5sum:
        return False, "亲, md5sum不能为空"
    md5sum_re = re.compile("[a-f0-9]{32}")
    if not md5sum_re.match(md5sum):
        return False, "亲, md5sum格式不正确，必须为32位16进制数"
    return True, ""


def validate_component_desc(component_desc):
    if not isinstance(component_desc, dict):
        return False, "亲, component_desc只能为字典格式"
    return True, ""
