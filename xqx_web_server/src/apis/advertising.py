# coding=utf-8
import datetime
import logging
import re

from apis.base import BaseApi
from models.aptm import Project
from models.common import AdvMedia
from utils import tools
from utils.permission import public_dev_login_required
from utils.tools import get_default_result
from utils import content_types
log = logging.getLogger('django')

class AdvApi(BaseApi):

    """
    广告管理
    """

    M = 1024 * 1024

    def _upload_media_file(self, request, adv):

        media_file_data = b''
        media_file = request.FILES.get("media_file", None)
        if not media_file:
            return False, "未上传文件", None

        file_name = media_file.name.lower().strip()
        suffix = tools.match_file_name_suffix(file_name)

        if suffix not in [".png", ".jpg", ".mp4"]:
            return False, "文件类型错误", None

        if suffix in [".png", ".jpg"]:
            adv.adv_type = "图片"
        else:
            adv.adv_type = "视频"

        for chunk in media_file.chunks():
            media_file_data += chunk

            if len(media_file_data) > self.M * 50:
                return False, "上传文件错误(文件大小超过50M)", None

        adv.media_file.new_file(content_type=content_types.match(file_name), filename=file_name)
        adv.media_file.write(media_file_data)
        adv.media_file.close()

        return True, "", None

    def mgr_submit_adv(self, adv_name="", company_name="", start_date="", end_date="", weight=1, project_ids=[]):
        """
        管理员上传广告信息
        :param adv_name: T-str, 广告名称
        :param company_name: T-str, 公司名称
        :param start_date: T-str, 开始时间(格式 2017/01/01)
        :param end_date: T-str, 截止时间(格式 2017/01/01)
        :param weight: T-int, 权重倍数
        :param project_ids: T-list, 社区项目编号列表
        :return: data->{}

        :notice: 上传文件 FILES['media_file']
        """
        result = get_default_result()

        adv = AdvMedia()
        adv.name = adv_name
        adv.company_name = company_name
        adv.weight = weight

        if not start_date or not end_date:
            return result.setmsg("未填写有效期", 3)

        start_date = datetime.datetime.strptime(start_date + " 00:00:00", '%Y/%m/%d %H:%M:%S')
        end_date = datetime.datetime.strptime(end_date + " 23:59:59", '%Y/%m/%d %H:%M:%S')

        if end_date < start_date:
            return result.setmsg("有效期范围不正确", 3)

        adv.start_at = start_date
        adv.end_at = end_date

        projects = Project.objects(id__in=project_ids)
        adv.projects = projects

        flag, msg, o = self._upload_media_file(self.request, adv)
        if not flag:
            return result.setmsg(msg, 3)

        adv.saveEx()
        result.setmsg("上传广告信息完成")
        return result

    def get_adv(self, adv_id):
        """
        通过ID获取广告对象
        :param adv_id: T-str, 广告对象ID
        :return:  data->{adv:#obj}
        """
        result = get_default_result()
        adv = AdvMedia.objects(id=adv_id).first()
        if not adv:
            return result.setmsg("记录不存在", 3)

        result.setdata("adv", adv.outputEx())
        return result

    def mgr_edit_adv(self, adv_id, adv_name="", company_name="", start_date="", end_date="", weight=0, project_ids=[]):
        """
        管理员编辑广告信息
        :param adv_id: T-str, 广告对象ID
        :param adv_name: T-str, 广告名称
        :param company_name: T-str, 公司名称
        :param start_date: T-str, 开始时间(格式 2017/01/01)
        :param end_date: T-str, 截止时间(格式 2017/01/01)
        :param weight: T-int, 权重倍数
        :param project_ids: T-list, 社区项目编号列表
        :return: data->{}
        """

        result = get_default_result()
        adv = AdvMedia.objects(id=adv_id).first()
        if not adv:
            return result.setmsg("编辑失败，记录不存在", 3)

        if adv_name: adv.name = adv_name
        if company_name: adv.company_name = company_name
        if weight: adv.weight = int(weight)
        if project_ids: adv.projects = Project.objects(id__in=project_ids)

        if not start_date or not end_date:
            return result.setmsg("未填写有效期", 3)

        start_date = datetime.datetime.strptime(start_date + " 00:00:00", '%Y/%m/%d %H:%M:%S')
        end_date = datetime.datetime.strptime(end_date + " 23:59:59", '%Y/%m/%d %H:%M:%S')

        if end_date < start_date:
            return result.setmsg("有效期范围不正确", 3)

        adv.start_at = start_date
        adv.end_at = end_date

        adv.saveEx()

        result.setmsg("编辑完成")
        return result

    @public_dev_login_required
    def gate_get_advs(self):
        """
        门口机获取广告列表
        :return: data->{collection:[...]}
        """
        result = get_default_result()
        dev = self._get_login_device()
        now = datetime.datetime.now()
        advs = AdvMedia.objects(projects__in=[dev.project], start_at__lte=now, end_at__gte=now)

        def __ex_fun(adv, obj):
            media_file, media_file_infos = adv.media_file, {}
            obj['media_file_infos'] = media_file_infos
            if not media_file: return

            media_file_infos['filename'] = media_file.filename
            media_file_infos['md5'] = media_file.md5
            media_file_infos['length'] = media_file.length
            media_file_infos['url'] = "%s/download/advmedia/%s" % (self._get_http_scheme_host, media_file._id)

        result.data_collection_output(advs, exclude_fileds=['projects'], ex_fun=__ex_fun)

        return result

    def mgr_list_advs(self, company_name_like="", pager={}):
        """
        管理员查询广告列表
        :param company_name_like: T-str, 公司名称
        :param pager: T-obj#{page_size:#int, page_no:#int} 分页信息
        :return: data->{collection:[...]}
        """
        result = get_default_result()
        advs = AdvMedia.objects().order_by("-created_at")
        if company_name_like:
            advs = advs.filter(company_name__contains=company_name_like)

        result["data"] = tools.paginate_query_set(advs, pager=pager)
        return result

    def remove_adv(self, adv_id):
        """
        管理员删除指定的广告
        :param adv_id: T-str, 广告对象ID
        :return: data->{}
        """
        result = get_default_result()
        adv = AdvMedia.objects(id=adv_id).first()
        if not adv:
            return result.setmsg("删除失败，记录不存在", 3)
        if adv.media_file:
            adv.media_file.delete()

        adv.delete()
        result.setmsg("删除完成")
        return result


