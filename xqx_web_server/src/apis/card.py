#coding=utf-8
import csv
import logging
import re

import datetime
from io import StringIO, BytesIO

from django.http import HttpResponse

from apis.base import BaseApi
from apis.gate import GateApi
from models.aptm import Room
from models.common import AccessCard
from utils import tools
from utils.permission import wuey_user_login_required
from utils.tools import get_default_result, paginate_query_set

log = logging.getLogger('django')


class AccessCardApi(BaseApi):

    def _parse_aptm_codes_to_owner_name(self, aptm_codes):

        return "-".join([str(x) for x in aptm_codes[0:4]]) + "{:0>2}".format(aptm_codes[4])

    def _mk_expiry_date(self, expiry_date):
        """
        创建过期日期
        :param expiry_date:
        :return:
        """
        _expiry_date = tools.longlong_date()  # default

        if expiry_date:
            try:
                _expiry_date = datetime.datetime.strptime("%s 23:59:59" % expiry_date, "%Y/%m/%d %H:%M:%S")

            except Exception as e:
                return None, "参数expiry_date=%s错误" % expiry_date

            if (_expiry_date - datetime.datetime.now()).days < 1:
                return None, "有效期不能少于一天"

        return _expiry_date, ""

    @classmethod
    def _notify_gates(cls, project):

        GateApi._remove_sync_cards_cache(str(project.id))
        msg_type = "gate_card_sync"
        extras = {"msg_type": msg_type}
        tools.send_push_message(tags="%s_%s" % (project.id, msg_type), extras=extras)


    @wuey_user_login_required
    def unregister_card(self, card_id):
        """
        注销卡片
        :param card_id: T-string, card object id
        :return:
        """
        result = get_default_result()
        user = self._get_login_user()
        project = user.project
        card = AccessCard.objects(id=card_id, project=project).first()
        if not card:
            return result.setmsg('卡号不存在', 3)

        card.is_valid = False  # 逻辑删除
        card.saveEx()

        result.setmsg('注销[%s]成功' % card.card_no)
        self._notify_gates(project)
        return result

    @wuey_user_login_required
    def register_wuye_work_card(self, card_no, card_type="manager", owner_name="", expiry_date=""):
        """
        添加物业卡, 包括物业人员，及其它工作人员的门禁卡
        :param card_no: T-string, 卡片编号 6~10 位
        :param card_type: T-string, 卡类型 可选值 manager|worker
        :param owner_name:
        :param expiry_date:  T-string,  过期日期 如:2016/01/08
        :return:
        """
        result = get_default_result()
        user = self._get_login_user()
        project = user.project

        _expiry_date, msg = self._mk_expiry_date(expiry_date)

        if not _expiry_date: return result.setmsg(msg, 3)

        if not card_no or not re.findall(r"^\d{6,10}$", card_no):
            return result.setmsg("卡号信息不正确", 3)

        card = AccessCard.objects(project=project, card_no=card_no).first()

        if card and card.is_valid:
            return result.setmsg("此卡号已被使用", 3)

        if not card:
            card = AccessCard(card_no=card_no)

        card.set_attrs(domain=project.domain, project=project, card_type=card_type, owner_name=owner_name)
        card.set_attrs(is_valid=True, expiry_date=_expiry_date, aptm_uuid="")

        card.saveEx()

        result.setmsg('成功添加门禁卡')
        self._notify_gates(project)
        return result

    @wuey_user_login_required
    def register_resident_card(self, card_no, apm_fuuid, expiry_date=""):
        """
        添加 住户卡,支持同时添加多个卡号(多卡号用,分隔)
        :param card_no:  T-string, 卡片编号 6~10 位
        :param apm_fuuid:  T-string,  房号, 如: 1-2-3-4-5 -> 1期2栋3单元405号
        :param expiry_date:  T-string,  过期日期 如:2016/01/08
        :return:
        """
        result = get_default_result()
        user = self._get_login_user()
        project = user.project

        aptm_codes = tools.parse_apartment_fuuid(apm_fuuid)

        if not aptm_codes or 0 in aptm_codes:
            return result.setmsg("房号信息不正确", 3)

        if not re.findall("^[\s,\d]+$", card_no):
            return result.setmsg("卡号信息不正确", 3)

        douhao_count = len(re.findall(",", card_no))
        card_no_list = re.findall("\d{6,10}", card_no)

        if not card_no_list or not douhao_count != len(card_no_list):
            return result.setmsg("卡号信息不正确", 3)

        _expiry_date, msg = self._mk_expiry_date(expiry_date)

        if not _expiry_date: return result.setmsg(msg, 3)

        aptm_uuid = tools.parse_aptm_codes_to_uuid(aptm_codes)
        aptm = Room.objects(aptm_uuid=aptm_uuid).first()

        if not aptm:
            return result.setmsg("指定的房间不存在", 3)

        def _add_card(card_no):
            card = AccessCard.objects(project=project, card_no=card_no).first()

            if not card:
                card = AccessCard(card_no=card_no)

            card.set_attrs(domain=project.domain, project=project, is_valid=True)
            card.set_attrs(card_type='resident', aptm_uuid=aptm_uuid)
            card.set_attrs(owner_name=self._parse_aptm_codes_to_owner_name(aptm_codes), expiry_date=_expiry_date)

            card.saveEx()

        for card_no in card_no_list:
            _add_card(card_no)

        result.setmsg('成功添加住户门禁卡')
        self._notify_gates(project)
        return result

    @wuey_user_login_required
    def list_cards(self, card_type="", card_no_like="", owner_name_like="", sort_type="-updated_at", pager={}):
        """
        根据类型及卡号查询
        @param card_type:    卡片类型
        :param card_no_like: T-string, 模糊匹配卡号
        :param owner_name_like: T-string, 模糊匹配持卡人
        :param sort_type: T-string, 排序
        :param pager: T-#obj, 分页
        @return:
        """
        result = get_default_result()
        user = self._get_login_user()
        project = user.project

        cards = AccessCard.objects(project=project, is_valid=True).order_by(sort_type)

        if card_type:
            cards = cards.filter(card_type=card_type)

        if card_no_like:
            cards = cards.filter(card_no__contains=card_no_like)

        if owner_name_like:
            cards = cards.filter(owner_name__contains=owner_name_like)

        result["data"] = paginate_query_set(cards, pager)
        return result

    @wuey_user_login_required
    def list_resident_cards(self, aptm_fuuid_like="", sort_type="-updated_at", pager={}):
        """
        查询相关的业主卡
        :param aptm_fuuid_like: T-string, 房间号匹配模式， 如 1-39-0-1-1 ，其中0表示任意
        :param sort_type: T-string, 排序
        :param pager: T-#obj, 分页
        :return: data->{collection:[...], pagination:{...}}
        """
        result = get_default_result()
        user = self._get_login_user()
        project = user.project

        cards = AccessCard.objects(project=project, card_type='resident', is_valid=True).order_by(sort_type)

        _aptm_uuid_like = ''
        if aptm_fuuid_like:
            codes = tools.parse_apartment_fuuid(aptm_fuuid_like)
            if codes:
                _aptm_uuid_like = tools.parse_codes_to_aptm_uuid_pattern(codes)

        log.debug("_aptm_uuid_like:%s", _aptm_uuid_like)

        if _aptm_uuid_like:
            cards = cards.filter(__raw__={"aptm_uuid": {"$regex": _aptm_uuid_like}})

        result["data"] = paginate_query_set(cards, pager=pager)
        return result


class ImportExportCardApi(BaseApi):

    APTM_FORMAT = "(\d{1,3})-(\d{1,3})-(\d{1,3})-(\d{3,4})"

    def _check_upload_file(self):
        """
        csv文件检查
        :return:
        """
        f_max_size = 1024 * 800   # 800K

        files = self.request.FILES.getlist('myfiles')

        if not files:
            return False, "未上传.csv文件"

        f = files[0]

        if not re.findall(r"\.csv", f.name, re.IGNORECASE):
            return False, "文件格式不正确,请选择.csv文件"

        if f.size > f_max_size:
            return False, "上传的.csv文件过大"

        return True, f

    def _check_csv_content(self, data_list):

        """
        检查文件内容，格式，重复记录
        :param data_list:
        :return message_list 错误消息列表
        """
        pattern = "^(业主卡|物业卡|工作卡),((%s)|([^\s]{2,20})),([0-9/]+)$" % self.APTM_FORMAT
        empty_line = "^[\s,]+$"
        line_no = 1
        from collections import Counter
        codes_list = []
        message_list = []
        for data in data_list[1:]:
            line_no += 1
            card_type = data.get('type', '').strip()
            card_owner = data.get('owner', '').strip()
            codes = str(data.get('codes', '')).strip()

            line = ",".join([card_type, card_owner, codes])
            if re.findall(empty_line, line): continue
            if not re.findall(pattern, line):
                message_list.append("第%d行错误" % line_no)
                continue

            if card_type == "业主卡" and not re.findall(self.APTM_FORMAT, card_owner):
                message_list.append("第%d行错误" % line_no)
                continue

            _codes = re.findall("\d+", codes)

            if not _codes: message_list.append("第%d行错误" % line_no)

            _code_err = False
            for _c in _codes:
                if not (6 <= len(_c) <= 10):
                    _code_err = True
                else:
                    codes_list.append(_c)

            if _code_err:
                message_list.append("第%d行错误" % line_no)
                continue

        repeats = []

        for x in Counter(codes_list).items():
            if x[1] > 1: repeats.append(x[0])

        if repeats:
            message_list.append("出现重复的卡号: %s" % ("\n".join(repeats)))

        return message_list

    def _parse_csv_file(self, csv_data):
        """
        解析 csv 文件数据
        :param csv_data:
        :return:
        """
        bio = BytesIO()
        for chunk in csv_data.chunks():
            bio.write(chunk)

        bio.seek(0)

        try:
            bio_content = bio.getvalue().decode('utf-8')
        except UnicodeDecodeError as e:
            bio.seek(0)
            bio_content = bio.getvalue().decode('gb2312')
        finally:
            bio.close()

        sio = StringIO()
        sio.write(bio_content)
        sio.seek(0)

        data = []
        try:
            reader = csv.DictReader(sio, fieldnames=['type', 'owner', 'codes'])
            for item in reader:
                data.append(item)
            return True, data

        except Exception as e:
            log.exception(e)
            return False, '导入失败，无法读取文件内容'

        finally:
            sio.close()

    @classmethod
    def _parse_resident_card_owner_to_aptm_uuid(cls, card_owner):
        xx = re.findall(cls.APTM_FORMAT, card_owner)[0]

        # 注 xx[3] 为层及房号部分 104 -> 1层4号房
        codes = xx[0:3] + re.findall('(\d{1,3})(\d{2})$', xx[3])[0]
        aptm_uuid = tools.parse_aptm_codes_to_uuid(codes)
        return aptm_uuid

    @classmethod
    def _import_cards_to_db(cls, data_list, project):
        count = 0

        for data in data_list:
            card_type = data.get('type', '').strip()
            codes = str(data.get('codes', '')).strip()
            card_owner = data.get('owner', '').strip()

            owner_name = card_owner

            card_no_list = re.findall('\d+', codes)
            if not card_no_list: continue

            for card_no in card_no_list:
                new_card = AccessCard.objects(card_no=card_no, project=project).first()

                if not new_card:
                    new_card = AccessCard(project=project, card_no=card_no)

                new_card.aptm_uuid = ""
                new_card.expiry_date = datetime.datetime.strptime("2200/01/01", '%Y/%m/%d')

                if card_type == '物业卡':
                    new_card.card_type = 'manager'

                elif card_type == '工作卡':
                    new_card.card_type = 'worker'

                elif card_type == '业主卡':
                    aptm_uuid = cls._parse_resident_card_owner_to_aptm_uuid(card_owner)
                    new_card.set_attrs(card_type='resident', aptm_uuid=aptm_uuid)

                new_card.set_attrs(domain=project.domain, project=project, is_valid=True)
                new_card.owner_name = owner_name
                new_card.saveEx()

                count += 1

        return count

    @wuey_user_login_required
    def import_cards(self):
        """
        从 csv 文件, 导入发卡数据
        :return:
        """
        result = get_default_result()
        user = self._get_login_user()
        project = user.project

        flag, res = self._check_upload_file()
        if not flag:
            return result.setmsg(res, 3)

        flag2, res2 = self._parse_csv_file(res)
        if not flag2:
            return result.setmsg(res2, 3)

        error_message_list = self._check_csv_content(res2)
        if error_message_list:
            return result.setmsg("\n".join(error_message_list), 3)

        count = 0
        try:
            count = self._import_cards_to_db(res2, project)
        except Exception as e:
            log.exception(e)

        result.setmsg('导入完成, 变更%s条卡记录' % count)

        if count:
            AccessCardApi._notify_gates(project)

        return result

    @wuey_user_login_required
    def export_cards(self):
        """
        导出发卡数据
        @return:
        """

        user = self._get_login_user()
        project = user.project
        cards = AccessCard.objects(project=project, is_valid=True).order_by("card_type", "owner_name")

        response = HttpResponse(content_type="application/octet-stream")
        fname = "access_cards_%s.csv" % datetime.datetime.now().strftime("%y%m%d_%H%M")
        response['Content-Disposition'] = 'attachment;filename="%s"' % fname

        # csv write_out:
        writer = csv.DictWriter(response, fieldnames=['type', 'owner', 'codes'])
        csv_title = dict(type='类型', owner='持卡人', codes='卡号')
        writer.writerow(csv_title)

        # 写数据
        card_infos = []
        card_types = dict(AccessCard.TYPE_CHOICES)
        for c in cards:

            item = dict(
                type=card_types.get(c.card_type, ''),
                owner=c.owner_name,
                codes="%s" % c.card_no,
            )
            card_infos.append(item)

        writer.writerows(card_infos)
        return response



