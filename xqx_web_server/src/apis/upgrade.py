# coding=utf-8
import json

import re

from apis.base import BaseApi
from utils import tools
from utils.tools import get_default_result, rds_api_cache
from models.common import QDVersion
from conf.qd_conf import CONF
from utils import content_types
import logging
log = logging.getLogger('django')


class AgwUpgradeApi(BaseApi):
    M = 1024 * 1024
    ftypes = dict(sw=1, res=2, wifi=3)

    @rds_api_cache(ex=60, think_session=False)
    def _get_release_bin_files(self):
        """
        获取最新发布版本(sw, res)信息
        :return:[[id,fi_tye,fi_size,chksum,version],...]
        """
        sw = QDVersion.get_newest_version(component_type="sw")
        res = QDVersion.get_newest_version(component_type="res")

        files = []
        result = []

        if sw: files.append(sw)
        if res: files.append(res)

        for uf in files:
            result.append(self._get_uf_info(str(uf.id)))

        return result

    @rds_api_cache(ex=60*10, think_session=False)
    def _get_uf_info(self, uf_id):
        """
        获取指定版本的信息
        :param uf_id: T-str, 版本ID
        :return: [id,fi_tye,fi_size,chksum,version]
        """
        ver = QDVersion.objects(id=uf_id).first()
        if ver and ver.bin_file:
            ftype = self.ftypes.get(ver.component_type)
            fdata = self._get_whole_file_bytes(uf_id)
            chksum = tools.bytes_check_sum(fdata)
            return ["%s" % ver.id, ftype, len(fdata), chksum, ver.version]

        return []

    @rds_api_cache(ex=60*30, think_session=False)
    def _get_whole_file_bytes(self, uf_id):
        """
        返回指定升级文件的字节内容
        :param uf_id: T-string, 升级文件ID
        :return: T-bytes
        """
        uf = QDVersion.objects(id=uf_id).first()
        file_data = uf.bin_file.read()
        return file_data

    @rds_api_cache(ex=60*30, think_session=False)
    def _request_data_section(self, uf_id, offset=0, step=512):
        """
        请求文件片段
        [请参考 PayloadDataSection]
        :param uf_id: T-string, 升级文件ID
        :param offset: T-int, 起始
        :param step: T-int, 步长
        :return: [文件ID,文件大小,数据长度,数据chksum,累计数据长度,数据]
        """
        ver = QDVersion.objects(id=uf_id).first()

        if not ver:
            return False

        fdata = self._get_whole_file_bytes(uf_id)
        data = fdata[offset:offset + step]

        data_size = len(data)
        data_chksum = tools.bytes_check_sum(data)
        range_length = offset + data_size

        section = [str(ver.id), len(fdata), data_size, data_chksum, range_length, data]

        return section

    @classmethod
    @rds_api_cache(ex=60, think_session=False)
    def _get_wifi_last_version_file_bytes(cls):
        """
        读取WIFI模块升级文件内容
        :return: T-bytes
        """
        ver = QDVersion.get_newest_version(component_type='wifi')
        if not ver: return b''
        file_data = cls()._get_whole_file_bytes("%s" % ver.id)
        return file_data

    @classmethod
    def _get_wifi_last_version_infos(cls):
        """
        报警网关检测Wifi模块升级的信息
        :return: T-#list[host,port,version]
        :notice: 没有升级版本时，返回空None
        """
        wos = CONF.get("wifi_ota_server")
        ver = QDVersion.get_newest_version(component_type="wifi")
        if not ver: return None

        return [3, ver.version, wos[0], wos[1]]


class ComponentUpgradeApi(BaseApi):
    """
    组件升级接口类
    """
    M = 1024 * 1024

    @classmethod
    def _write_file(cls, src, bin_file, max_size):
        if not src:
            return False, "未检测到升级文件，请重新上传", None

        if src.size > max_size:
            return False, "上传文件错误, 不能超过%dM" % int(max_size / cls.M)

        file_name = src.name.lower().strip()
        file_data = b''
        for chunk in src.chunks():
            file_data += chunk

        if not file_data:
            return False, "不能上传空文件", None

        bin_file.new_file(content_type=content_types.match(file_name), filename=file_name)
        bin_file.write(file_data)
        bin_file.close()

        ret = {
            "md5sum": bin_file.md5
        }
        return True, "", ret

    @classmethod
    def _read_json_file(cls, src):
        if not src:
            return False, "未检测到json文件", None

        if src.size > 10240:
            return False, "json文件错误, 文件大小超过10k", None

        file_data = b''
        for chunk in src.chunks():
            file_data += chunk

        json_str = file_data.decode('utf-8')
        if not json_str:
            return False, "json文件内容不能为空", None
        try:
            json_info = json.loads(json_str)
        except Exception as e:
            return False, "json文件解析错误", None

        if not isinstance(json_info, dict):
            return False, "json文件内容只能是字典", None

        if json_info.keys() != set(["version", "md5sum", "component_type", "package_name", "component_desc"]):
            return False, "json key 约束错误", None

        if not re.findall("^\w{2,30}$", json_info.get("component_type", "")):
            return False, "component_type错误", None

        if not re.findall("^[0-9a-f]{32}$", json_info.get("md5sum", "")):
            return False, "md5sum错误", None

        if not re.findall("^\d{1,3}\.\d{1,3}.\d{1,3}$", json_info.get("version", "")):
            return False, "version错误", None

        return True, "", json_info


    def check_upgrade(self, project_id=None, component_type=None):
        """
        检测升级版本
        :param project_id: 小区id, T-string: "5673d4dc2c923a0ac450628d"(24位数字), 可选参数，手机app可不传
        :param component_type: 组件类型, T-string: eg: "little_elephant"
        :return: data - {"qd_version": {...}}
        """
        result = get_default_result()
        ver = QDVersion.get_newest_version(component_type=component_type)

        if not ver: return result.setmsg("当前无任何版本信息", 3)

        url = "%s/download/upgrade/%s/%s/%s" % (self._get_http_scheme_host(), ver.component_type, ver.id, ver.filename)
        _version_info = {
            "name": ver.name, "version": ver.version, "md5sum": ver.md5sum,
            "component_type": ver.component_type, "component_desc": ver.component_desc,
            "filename": ver.filename,
            "url": url
        }

        result.data['qd_version'] = _version_info
        return result

    def add_version(self):
        """
        添加组件版本
        上传两个文件，名称分别是 json_file, bin_file
        :return:data -> {}
        """
        result = get_default_result()
        json_file = self.request.FILES.get("json_file", None)
        flg, msg, json_info = self._read_json_file(json_file)
        if not flg: return result.setmsg(msg, 3)

        component_type = json_info.get("component_type", "")
        version_code = "".join(["{:0>3}".format(c) for c in re.findall("\d+", json_info.get('version', ""))])

        if QDVersion.is_exist_obj(component_type=component_type, version_code=version_code):
            return result.setmsg("已经存在相同的版本", 3)

        newest_ver = QDVersion.get_newest_version(component_type=component_type)
        if newest_ver and version_code <= newest_ver.version_code:
            return result.setmsg("当前提交的版本小于有效版本", 3)

        _cur_vers = QDVersion.objects(component_type=component_type, release_status="releaseing")

        ver = QDVersion()
        bin_file = self.request.FILES.get("bin_file", None)
        write_flag, msg, write_ret = self._write_file(bin_file, ver.bin_file, self.M * 100)
        if not write_flag: return result.setmsg(msg, 3)

        if json_info['md5sum'] != write_ret['md5sum']:
            ver.bin_file.delete()
            return result.setmsg("md5值与文件不匹配", 3)

        ver.set_attrs(version=json_info.get("version"), version_code=version_code)
        ver.set_attrs(filename=bin_file.name, md5sum=json_info.get("md5sum"))
        ver.set_attrs(component_type=json_info.get("component_type"), component_desc=json_info.get("component_desc", {}))
        ver.set_attrs(name=json_info.get('package_name'))

        _cur_vers.update(release_status="history")
        ver.saveEx()
        result.setmsg("版本发布成功")
        return result

    def get_verison_by_filter(self, component_type="", release_status="releaseing", pager={}):
        """
        检索版本信息
        :param component_type: 组件类型, T-string
        :param release_status: 版本状态， T-string
        :param pager: 分页信息, T-dict
        :return: data -> {collection:[...]}
        """
        result = get_default_result()
        versions = QDVersion.objects().order_by("component_type", "-release_at")

        if component_type:
            versions = versions.filter(component_type=component_type)
        if release_status:
            versions = versions.filter(release_status=release_status)

        result['data'] = tools.paginate_query_set(versions, pager)
        return result


    def remove_verison(self, ver_id):
        """
        删除/停用版本
        :param ver_id: T-str, 版本ID
        :return: data->{}
        """
        result = get_default_result()
        ver = QDVersion.objects(id=ver_id).first()

        ver.release_status = "history"
        ver.saveEx()

        return result.setmsg("版本取消完成")

