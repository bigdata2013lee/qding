# --*-- coding:utf8 --*---

from apps.brake.classes.Brake_Machine import Brake_Machine
import xlwt
from settings.const import CONST
from settings.default import BASE_DIR
import os
from apps.common.utils.sentry_date import get_datatime, get_str_time_by_timestamp


def run():
    brake_machine_list = [brake.get_brake_info() for brake in Brake_Machine.objects(status='1')]
    dump_brake_machine_data(brake_machine_list, 'brake_machine')


def dump_lately_pass_machine():
    raw_query = {"status": "1", "updated_time": {"$lte": get_datatime(-30)}}
    brake_machine_list = [brake.get_brake_info() for brake in Brake_Machine.objects(__raw__ = raw_query)]
    dump_brake_machine_data(brake_machine_list, 'brake_machine')


def dump_brake_machine_data(brake_machine_list, filename):
    writeObj = xlwt.Workbook()
    qr_data = writeObj.add_sheet(u'门禁数据', cell_overwrite_ok=True)
    qr_data.write(0, 0, u'省份')
    qr_data.write(0, 1, u'城市')
    qr_data.write(0, 2, u'小区')
    qr_data.write(0, 3, u'位置')
    qr_data.write(0, 4, u'mac')
    qr_data.write(0, 5, u'固件版本')
    qr_data.write(0, 6, u'硬件版本')
    qr_data.write(0, 7, u'门级别')
    qr_data.write(0, 8, u'最近通行时间')
    qr_data.write(0, 9, u'状态')

    x = 1
    for brake_machine_dic in brake_machine_list:
        position = brake_machine_dic.get("position", {}) or {}
        province = position.get('province', "") or ""
        city = position.get("city", "") or ""
        project_list = position.get("project_list", []) or []
        project = project_list[0].get("project", "") if len(project_list) == 1 else ""
        position_str = brake_machine_dic.get("position_str", "") or ""
        mac = brake_machine_dic.get("mac", "") or ""
        version = brake_machine_dic.get("version", "") or ""
        hardware_version = brake_machine_dic.get("hardware_version", "") or ""
        level = brake_machine_dic.get("level", "") or ""
        updated_time_str = get_str_time_by_timestamp(brake_machine_dic.get("updated_time", 0) or 0)
        online_status_str = brake_machine_dic.get("online_status_str", "") or ""

        qr_data.write(x, 0, province)
        qr_data.write(x, 1, city)
        qr_data.write(x, 2, project)
        qr_data.write(x, 3, position_str)
        qr_data.write(x, 4, mac)
        qr_data.write(x, 5, version)
        qr_data.write(x, 6, hardware_version)
        qr_data.write(x, 7, level)
        qr_data.write(x, 8, updated_time_str)
        qr_data.write(x, 9, online_status_str)
        x += 1
    excel_dir = "%s/uploads/dump_to_excel" % BASE_DIR
    if not os.path.exists(excel_dir): os.makedirs(excel_dir)
    writeObj.save("%s/%sbrake_machine_data.xls" % (excel_dir, filename))
    return "%suploads/dump_to_excel/%sbrake_machine_data.xls" % (CONST['base']['host'], filename)
