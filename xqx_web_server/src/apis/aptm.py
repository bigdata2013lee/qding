#coding=utf8
import csv
import datetime
import logging

import re

from io import BytesIO, StringIO

from apis.base import BaseApi
from conf.qd_conf import CONF
from models.device import AlarmGateway
from utils import tools
from utils.qd import QdRds
from utils.tools import paginate_query_set, rds_api_cache
from utils.permission import app_user_login_required, common_login_required, wuey_user_login_required, \
    mgr_login_required
from utils.tools import get_default_result
from models.aptm import Project, Room, PCity
from apis.pcity import PCityApi

log = logging.getLogger('django')

class AptmQueryApi(BaseApi):


    def get_project(self, project_id):
        """
        获取社区项目
        :param project_id: T-string, 社区项目ID
        :return: data->{project:#obj}
        """

        result = get_default_result()
        project = Project.objects(id=project_id).first()
        if not project: return result.setmsg("未找到社区项目", 3)

        result.data['project'] = project.outputEx()
        return result


    def list_projects(self, pcity_id, pcity_type="c"):
        """
        根据省/市，查询楼盘项目
        :param pcity_id: T-string, 省市ID
        :param pcity_type: T-string, 省市ID类型， 可选的值 p-省 c-市
        :return: data ->  {collection:[...]}
        """
        result = get_default_result()
        ccity_ids = []
        if pcity_type == 'c': ccity_ids = [pcity_id]
        elif pcity_type == 'p': ccity_ids = PCityApi()._get_ccity_ids(pcity_id)

        projects = Project.objects(ccity_id__in=ccity_ids)
        for project in projects:
            result.data_collection.append(project.outputEx())

        return result

    @rds_api_cache(120, think_session=False)
    def list_phases(self, project_id):
        """
        列出某楼盘项目下的组团(期)
        :param project_id: T-string, 楼盘项目ID
        :return: data ->  {collection:[...]}
        """
        result = get_default_result()
        rooms = Room.objects(project=project_id)
        result.data_collection = []
        temp_dict = {}
        for room in rooms:
            locs = room.get_locs()
            temp_dict[int(locs.get("phase", "0"))] = "%s期" % locs.get("phase", "0")

        _list = [{"code": k, "name": v} for k, v in temp_dict.items()]
        result.data_collection = _list

        return result

    @rds_api_cache(120, think_session=False)
    def list_buildings(self, project_id, phase_no):
        """
        列出某组团(期)下的楼栋
        :param project_id: T-string, 项目ID
        :param phase_no: T-int, 组团序号
        :return: data ->  {collection:[...]}
        """
        result = get_default_result()
        result.data_collection = []
        aptm_codes = [phase_no, 0, 0, 0, 0]
        aptm_uuid_pattern = tools.parse_codes_to_aptm_uuid_pattern(aptm_codes)
        rooms = Room.objects(project=project_id)
        rooms = rooms.filter(__raw__={"aptm_uuid": {"$regex": aptm_uuid_pattern}})

        temp_dict = {}
        for room in rooms:
            locs = room.get_locs()
            temp_dict[int(locs.get("building", "0"))] = "%s栋" % locs.get("building", "0")

        _list = [{"code": k, "name": v} for k, v in temp_dict.items()]
        result.data_collection = _list

        return result

    @rds_api_cache(120, think_session=False)
    def list_rooms(self, project_id, phase_no, building_no):
        """

        列出项目->组团->楼栋 下的所有房间对象
        :return: data ->  {collection:[...]}
        """

        result = get_default_result()

        rooms = Room.objects(project=project_id)
        aptm_codes = [phase_no, building_no, 0, 0, 0]
        aptm_uuid_pattern = tools.parse_codes_to_aptm_uuid_pattern(aptm_codes)
        rooms = rooms.filter(__raw__={"aptm_uuid": {"$regex": aptm_uuid_pattern}})

        for room in rooms:
            result.data_collection.append(room.outputEx())

        return result


    @common_login_required
    def query_rooms_for_wuye(self, phase_no=0, building_no=0, unit_no=0, aptm_short_code="", pager={}):
        """
        查询房间列表

        供物或AIO端 使用的接口

        :param phase_no: T-int, 期序号
        :param building_no: T-int, 栋序号
        :param unit_no: T-int, 单元序号
        :param aptm_short_code: T-str, 房间码
        :param pager: T-obj#{page_size:#int, page_no:#int} 分页
        :return: data->{collection:#list}
        """
        result = get_default_result()

        user = self._get_login_user()
        project = user.project

        rooms = Room.objects(project=project).order_by("aptm_uuid")
        codes = [phase_no, building_no, unit_no, 0, 0]

        if aptm_short_code:
            codes[3:] = tools.parse_aptm_short_code(aptm_short_code)

        aptm_uuid_pattern = tools.parse_codes_to_aptm_uuid_pattern(codes)
        rooms = rooms.filter(__raw__={"aptm_uuid": {"$regex": aptm_uuid_pattern}})

        result.data = paginate_query_set(rooms, pager=pager)
        return result


    @app_user_login_required
    def get_aptm_by_agw_mac(self, mac):
        """
        通过MAC获取绑定的房间信息
        :param mac: T-string, 网关设备MAC
        :return: data->{aptm:#obj}
        """
        result = get_default_result()
        agw = AlarmGateway.objects(mac=mac).first()
        if not agw or not agw.aptm:
            return result.setmsg("设备未绑定房间", 3)

        result.data["aptm"] = agw.aptm.outputEx()
        return result


    def _get_aptm_loc_infos(self, aptm_id, building=1, phase=1, project=1, ccity=1):
        """

        :param aptm_id:
        :return:
        """
        room = Room.objects(id=aptm_id).first()

        aptm_loc_infos={}
        aptm_locs = room.get_locs()
        aptm_loc_infos["aptm_id"] = str(room.id)
        aptm_loc_infos["aptm_locs"] = aptm_locs
        aptm_loc_infos["aptm_name"] = room.name

        aptm_loc_infos["project_id"] = str(room.project.id)
        aptm_loc_infos["project_name"] = room.project.name

        if ccity:
            _project = room.project
            aptm_loc_infos["ccity_id"] = "%s" % _project.ccity_id

            ccity_name = PCityApi().get_ccity(_project.ccity_id).get("data", {}).get("city", {}).get("cname", "")
            aptm_loc_infos["ccity_name"] = ccity_name

        return aptm_loc_infos


    def get_aptm_loc_infos_by_id(self, aptm_id):
        """
        通过房间ID，获取房间的位置信息
        :param aptm_id: T-string, 房间ID
        :return: data -> {"aptm_loc_infos":{...}}
        """
        result = get_default_result()
        aptm_loc_infos = AptmQueryApi()._get_aptm_loc_infos(aptm_id)
        result.setdata("aptm_loc_infos", aptm_loc_infos)
        return result


class AptmManageApi(BaseApi):

    def add_project(self, ccity_id, project):
        result = get_default_result()
        projct = Project(ccity_id="%s" % ccity_id)
        projct.name = project.get("name", "")
        projct.saveEx()
        return result

    @wuey_user_login_required
    def wy_add_room(self, phase_no=0, building_no=0, unit_no=0, floor_no=0, room_no=0):
        """
        提供给物业单个添加房间的接口

        :param phase: T-int, 单元序号
        :param building: T-int, 单元序号
        :param unit: T-string, 单元序号
        :param floor: T-string, 楼层序号
        :param room: T-string, 房间序号
        :return: data->{}
        """

        result = get_default_result()

        user = self._get_login_user()
        project = user.project
        q1_codes = [phase_no, building_no, 0, 0, 0]
        q2_codes = [phase_no, building_no, unit_no, floor_no, room_no]

        log.debug("%s", project.id)
        log.debug(tools.parse_codes_to_aptm_uuid_pattern(q1_codes))
        temp_aptm = Room.objects(project=project, aptm_uuid=re.compile(tools.parse_codes_to_aptm_uuid_pattern(q1_codes))).first()

        if not temp_aptm:
            return result.setmsg("没有此楼栋", 3)

        aptm = Room.objects(project=project, aptm_uuid=re.compile(tools.parse_codes_to_aptm_uuid_pattern(q2_codes))).first()
        if aptm:
            return result.setmsg("此房间已经存在", 3)

        aptm = Room(domain=temp_aptm.domain, project=temp_aptm.project)

        aptm.set_attrs(aptm_uuid=tools.parse_aptm_codes_to_uuid(q2_codes), pre_names=temp_aptm.pre_names)
        aptm.rebuild_aptm_name()
        aptm.saveEx()
        
        result.setmsg("添加房间完成")
        return result



class AptmImportExportApi(BaseApi):

    """
    房屋列表(.csv)导入
    """
    @mgr_login_required
    def import_csv(self, project_id):
        """
        为特定的社区项目，导入房屋信息文件
        :param project_id:
        :return:
        :notice: csv 文件内容格式示例
        ====================================
        phase,buliding,unit,floor,room
        3/三期,1,1/A单元,1-5;7-10,4
        3/三期,2,1/A单元,1-1;,4
        ====================================
        期栋单元，使用/+文字，附加说明名称， 楼层使用范围描述x-y，多个范围用;号隔开
        """
        result = get_default_result()

        csv_file = self.request.FILES.get("csv_file", None)
        if not csv_file:
            return result.setmsg("未上传文件", 3)

        flg, rows, msg = self._parse_csv_file(csv_file)
        rows = rows[1:]

        log.debug(rows)
        if not flg:
            return result.setmsg(msg, 3)

        project = Project.objects(id=project_id).first()
        if not project:
            return result.setmsg("未找到相应的社区项目", 3)

        flg, msg = self._validate_csv(rows=rows)
        if not flg: return result.setmsg(msg, 3)

        self._import(project, rows=rows)

        result.setmsg("导入房屋信息文件完成")
        return result

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
            reader = csv.DictReader(sio, fieldnames=['phase_cell', 'building_cell', 'unit_cell', 'floor_cell', 'room_cell'])
            for item in reader:
                data.append(item)
            return True, data, ""

        except Exception as e:
            log.exception(e)
            return False, [], '导入失败，无法读取文件内容'

        finally:
            sio.close()

    def _validate_csv(self, rows=[]):
        """
        逐行数据校验
        :param rows:
        :return:
        """
        msg = "文件内容格式错误,大致范围在%d行"
        row_no = 1
        for row in rows:
            log.debug(row)
            flg, row_info = self._pase_cells(row)
            if not flg: return False, msg % row_no

            phase_no = row_info.get("phase_no")
            building_no = row_info.get("building_no")
            unit_no = row_info.get("unit_no")
            floors = row_info.get("floors")
            room_amount = row_info.get("room_amount")

            if not 0 < phase_no < 100: return False, msg % row_no
            if not 0 < building_no < 100: return False, msg % row_no
            if not 0 < unit_no < 100: return False, msg % row_no
            if not 0 < room_amount < 100: return False, msg % row_no

            if not (min(floors) > 0 and max(floors) < 100): return False, msg % row_no
            row_no += 1

        return True, ""

    def _pase_cells(self, row={}):
        """
        把一行数据进行分析，提取所有数据
        :param row:
        :return:
        """
        phase_cell = row.get("phase_cell", "")
        building_cell = row.get("building_cell", "")
        unit_cell = row.get("unit_cell", "")
        floor_cell = row.get("floor_cell", "")
        room_cell = row.get("room_cell", "")

        row_info = {}
        if not phase_cell: return False, {}
        if not building_cell: return False, {}
        if not unit_cell: return False, {}
        if not floor_cell: return False, {}
        if not room_cell: return False, {}

        pbu_pattern = "^(\d+)(?:/(.*))?$"
        # pahse
        phase_find = re.findall(pbu_pattern, phase_cell)
        if not phase_find: return False, {}

        phase_no = int(phase_find[0][0])
        phase_name = phase_find[0][1].strip() or "%d期" % phase_no

        # building
        building_find = re.findall(pbu_pattern, building_cell)
        if not building_find: return False, {}

        building_no = int(building_find[0][0])
        building_name = building_find[0][1].strip() or "%d栋" % building_no

        # uinit
        unit_find = re.findall(pbu_pattern, unit_cell)
        if not unit_find: return False, {}

        unit_no = int(unit_find[0][0])
        unit_name = unit_find[0][1].strip() or "%d单元" % unit_no

        # floor
        sp_floor_list = re.findall("(\d+)-(\d+)", floor_cell)
        floors = []
        if not sp_floor_list: return False, {}

        for sp in sp_floor_list:
            start, end = int(sp[0]), int(sp[1]) + 1
            if not (start > 0 and end > start): return False, {}
            floors.extend(range(start, end))

        floors = list(set(floors))

        # room
        room_find = re.findall("^(\d+)$", room_cell)
        if not room_find: return False, {}
        room_amount = int(room_find[0][0])

        row_info.update(dict(phase_no=phase_no, phase_name=phase_name,
                             building_no=building_no, building_name=building_name,
                             unit_no=unit_no, unit_name=unit_name,
                             floors=floors, room_amount=room_amount))
        return True, row_info

    def _import(self, project, rows=[]):
        """
        导入房屋列表
        :param project:
        :param rows:
        :return:
        """

        for row in rows:
            flg, row_info = self._pase_cells(row)
            if not flg: continue

            phase_no, phase_name = row_info.get("phase_no"), row_info.get("phase_name")
            building_no, building_name = row_info.get("building_no"), row_info.get("building_name")
            unit_no, unit_name = row_info.get("unit_no"), row_info.get("unit_name")

            _locs_list = []
            for _floor_no in row_info.get("floors"):
                for _room_no in range(1, row_info.get("room_amount") + 1):
                    _locs_list.append((unit_no, _floor_no, _room_no))

            for unit_no, floor_no, room_no in _locs_list:

                aptm_uuid = tools.parse_aptm_codes_to_uuid([phase_no, building_no, unit_no, floor_no, room_no])

                aptm = Room.objects(project=project, aptm_uuid=aptm_uuid).first()

                if not aptm:
                    aptm = Room(domain=project.domain, project=project, aptm_uuid=aptm_uuid)

                aptm.pre_names["phase"] = phase_name
                aptm.pre_names["building"] = building_name
                aptm.pre_names["unit"] = unit_name

                aptm.name = "{0}{1}{2:0>2}室".format(unit_name, floor_no, room_no)
                aptm.saveEx()

        return True

    @wuey_user_login_required
    def wy_send_csv_file(self):
        """
        物业提交基础数据文件(csv)
        :return:
        """
        from utils import mail
        to_list = CONF.get("mail_sys_users")
        result = get_default_result()

        user = self._get_login_user()
        project = user.project

        csv_file_data = b''
        csv_file = self.request.FILES.get("csv_file", None)
        if not csv_file:
            return result.setmsg("未上传文件", 3)

        for chunk in csv_file.chunks():
            csv_file_data.write(chunk)

        content = """
            <html>
                <body>
                    项目ID: {0} <br/>
                    项目名称: {1} <br/>
                </body>
            </html>
        """.format(project.id, project.name)

        csv_file_name = "%s_%s.csv" % (project.name, datetime.datetime.now().strftime("%Y%m%d%H%M"))
        subject = "%s基础数据导入" % project.name
        mail.send_email(to_list, subject, content, attachments=[(csv_file_name, csv_file_data)])

        result.setmsg("成功提交社区房屋基础数据文件，请等待工作人员会审核。")
        return result



