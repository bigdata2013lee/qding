import xlwt
from settings.const import CONST
from settings.default import BASE_DIR
import os


def dump_qr_pass_data(qr_pass_data_list, filename):
    if not qr_pass_data_list: return ''
    writeObj = xlwt.Workbook()
    qr_pass = writeObj.add_sheet(u'通行数据', cell_overwrite_ok=True)
    qr_pass.write(0, 0, u'地区')
    qr_pass.write(0, 1, u'小区')
    qr_pass.write(0, 2, u'房号')
    qr_pass.write(0, 3, u'绑定手机')
    qr_pass.write(0, 4, u'类型')
    qr_pass.write(0, 5, u'时间')
    qr_pass.write(0, 6, u'刷码位置')
    qr_pass.write(0, 7, u'进/出')
    x = 1
    for qr_pass_data in qr_pass_data_list:
        qr_pass.write(x, 0, qr_pass_data['city'])
        qr_pass.write(x, 1, qr_pass_data['community'])
        qr_pass.write(x, 2, qr_pass_data['room'])
        qr_pass.write(x, 3, qr_pass_data['phone'])
        visit_type = u'业主'
        if (qr_pass_data['type'] == '1'): visit_type = u'访客'
        qr_pass.write(x, 4, visit_type)
        qr_pass.write(x, 5, qr_pass_data['created_time'])
        qr_pass.write(x, 6, qr_pass_data['position'])
        direction = u'出'
        if (qr_pass_data['direction'] == 'I'): direction = u'进'
        qr_pass.write(x, 7, direction)
        x += 1
    excel_dir = "%s/uploads/dump_to_excel" % BASE_DIR
    if not os.path.exists(excel_dir): os.makedirs(excel_dir)
    writeObj.save("%s/%sqr_pass_data.xls" % (excel_dir, filename))
    return "%suploads/dump_to_excel/%sqr_pass_data.xls" % (CONST['base']['host'], filename)


def dump_qr_data(qr_data_list, filename):
    if not qr_data_list: return ''
    writeObj = xlwt.Workbook()
    qr_data = writeObj.add_sheet(u'预约数据', cell_overwrite_ok=True)
    qr_data.write(0, 0, u'地区')
    qr_data.write(0, 1, u'小区')
    qr_data.write(0, 2, u'房号')
    qr_data.write(0, 3, u'绑定手机')
    qr_data.write(0, 4, u'预约时间')
    qr_data.write(0, 5, u'失效时间')
    qr_data.write(0, 6, u'来访目的')
    qr_data.write(0, 7, u'有效次数')
    qr_data.write(0, 8, u'已来访')
    x = 1
    for qr_data_dic in qr_data_list:
        qr_data.write(x, 0, qr_data_dic['city'])
        qr_data.write(x, 1, qr_data_dic['community'])
        qr_data.write(x, 2, qr_data_dic['room'])
        qr_data.write(x, 3, qr_data_dic['phone'])
        qr_data.write(x, 4, qr_data_dic['start_time'])
        qr_data.write(x, 5, qr_data_dic['end_time'])
        qr_data.write(x, 6, qr_data_dic['reason'])
        valid_num = u'无限次'
        if (str(qr_data_dic['valid_num']) != '-1'): valid_num = str(qr_data_dic['valid_num']) + u'次'
        qr_data.write(x, 7, valid_num)
        status = u'是'
        if (qr_data_dic['status'] == '0'): status = u'否'
        qr_data.write(x, 8, status)
        x += 1
    excel_dir = "%s/uploads/dump_to_excel" % BASE_DIR
    if not os.path.exists(excel_dir): os.makedirs(excel_dir)
    writeObj.save("%s/%sqr_data.xls" % (excel_dir, filename))
    return "%suploads/dump_to_excel/%sqr_data.xls" % (CONST['base']['host'], filename)


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
    x = 1
    for brake_machine_dic in brake_machine_list:
        province = brake_machine_dic.get('province', "") or ""
        city = brake_machine_dic.get("city", "") or ""
        project = brake_machine_dic.get("project", "") or ""
        position_str = brake_machine_dic.get("position_str", "") or ""
        mac = brake_machine_dic.get("mac", "") or ""
        version = brake_machine_dic.get("version", "") or ""
        hardware_version = brake_machine_dic.get("hardware_version", "") or ""
        level = brake_machine_dic.get("level", "") or ""
        pass_time = brake_machine_dic.get("updated_time_str", "") or ""
        qr_data.write(x, 0, province)
        qr_data.write(x, 1, city)
        qr_data.write(x, 2, project)
        qr_data.write(x, 3, position_str)
        qr_data.write(x, 4, mac)
        qr_data.write(x, 5, version)
        qr_data.write(x, 6, hardware_version)
        qr_data.write(x, 7, level)
        qr_data.write(x, 8, pass_time)
        x += 1
    excel_dir = "%s/uploads/dump_to_excel" % BASE_DIR
    if not os.path.exists(excel_dir): os.makedirs(excel_dir)
    writeObj.save("%s/%sbrake_machine_data.xls" % (excel_dir, filename))
    return "%suploads/dump_to_excel/%sbrake_machine_data.xls" % (CONST['base']['host'], filename)


def dump_brake_card_data(brake_card_list, filename):
    write_obj = xlwt.Workbook()
    sheet_obj = write_obj.add_sheet(u'卡片数据', cell_overwrite_ok=True)
    sheet_obj.write(0, 0, u'卡号')
    sheet_obj.write(0, 1, u'省份')
    sheet_obj.write(0, 2, u'城市')
    sheet_obj.write(0, 3, u'小区')
    sheet_obj.write(0, 4, u'楼栋')
    sheet_obj.write(0, 5, u'单元')
    sheet_obj.write(0, 6, u'房间')
    x = 1
    for card_obj in brake_card_list:
        card_no = card_obj.card_no
        card_area = card_obj.card_area[0] if len(card_obj.card_area) == 1 else {}
        province = card_area.get("province", "")
        city = card_area.get("city", "")
        project = card_area.get("project", "")
        build = card_area.get("build", "")
        unit = card_area.get("unit", "")
        room = card_area.get("room", "")
        sheet_obj.write(x, 0, card_no)
        sheet_obj.write(x, 1, province)
        sheet_obj.write(x, 2, city)
        sheet_obj.write(x, 3, project)
        sheet_obj.write(x, 4, build)
        sheet_obj.write(x, 5, unit)
        sheet_obj.write(x, 6, room)
        x += 1
    excel_dir = "%s/uploads/dump_to_excel" % BASE_DIR
    if not os.path.exists(excel_dir): os.makedirs(excel_dir)
    write_obj.save("%s/%sbrake_card_data.xls" % (excel_dir, filename))
    return "%suploads/dump_to_excel/%sbrake_card_data.xls" % (CONST['base']['host'], filename)
