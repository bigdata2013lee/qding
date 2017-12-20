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


def validate_version(version):
    if not version:
        return False, "version can not be empty"
    version = str(version)
    version_re = re.compile("^V\d(\.\d){2}$")
    if not version_re.match(version):
        return False, "version should like Vx.x.x"
    return True, ""


def validate_version_project_list(project_list):
    if not isinstance(project_list, list): return False, "project_list can only be list"
    for project_dict in project_list:
        if not isinstance(project_dict, dict): return False, "the member of project_list must dict"
        if project_dict.keys() != set(['province', 'city', 'project', 'outer_project_id', 'project_flag']):
            return False, "the member of project_list can only have keys province, city, project, outer_project_id, project_flag"
        project_dict['outer_project_id'] = str(project_dict['outer_project_id'])
    return True, ""


def validate_filename(filename):
    if not filename:
        return False, "文件名不能为空"
    filename = str(filename)
    filename_re = re.compile("^[a-zA-Z][a-zA-Z_0-9\.]+[a-zA-Z]$")
    if not filename_re.match(filename):
        return False, "文件名格式为xxx.xxx.xxx"
    return True, ""


def validate_position(position):
    if not isinstance(position, dict):
        return False, "position must be dict"
    if not position:
        return False, "position can not be empty"
    if position.keys() != set(['level', 'province', 'city', 'project_list']):
        return False, "position can only have keys level and province and city and project_list"
    if str(position['level']) not in ['2', '3', '4', '5']:
        return False, "level can only be 2 or 3 or 4 or 5"
    position['level'] = int(position['level'])
    if not isinstance(position['project_list'], list):
        return False, "project_list must be list"
    if len(position['project_list']) > 10:
        return False, "the length of project_list can not great than 10"
    if not position['project_list']:
        return False, "project_list can not be emtpy"
    for i in range(len(position['project_list'])):
        project_dict = position['project_list'][i]
        if not isinstance(project_dict, dict):
            return False, "project_list can only consist of dict"
        if project_dict.keys() != set(['project', 'group_list', 'outer_project_id']):
            return False, "the member of project_list can only have keys project and group_list and outer_project_id"
        if position['level'] == 2:
            position['project_list'][i]['group_list'] = []
        else:
            if not project_dict['group_list']:
                return False, "group_list can not empty while level not equal 2"
            if not isinstance(project_dict['group_list'], list):
                return False, "group_list must be list"
            if len(project_dict['group_list']) > 10:
                return False, "the length of group_list can not great than 10"
            for j in range(len(project_dict['group_list'])):
                group_dict = position['project_list'][i]['group_list'][j]
                if not isinstance(group_dict, dict):
                    return False, "group_list can only consist of dict"
                if group_dict.keys() != set(['group', 'build_list', 'outer_group_id']):
                    return False, "the member of group_list can only have keys group and outer_group_id and build_list"
                if position['level'] == 3:
                    position['project_list'][i]['group_list'][j]['build_list'] = []
                else:
                    if not group_dict['build_list']:
                        return False, "build_list can not empty while level great than 2"
                    if not isinstance(group_dict['build_list'], list):
                        return False, "build_list must be list"
                    if len(group_dict['build_list']) > 10:
                        return False, "the length of build_list can not great than 10"
                    for k in range(len(group_dict['build_list'])):
                        build_dict = position['project_list'][i]['group_list'][j]['build_list'][k]
                        if not isinstance(build_dict, dict):
                            return False, "build_list can only consist of dict"
                        if build_dict.keys() != set(['build', 'outer_build_id', 'unit_dict_list']):
                            return False, "the member of build_list can only have keys build and outer_build_id and unit_dict_list"
                        if position['level'] == 4:
                            position['project_list'][i]['group_list'][j]['build_list'][k]['unit_dict_list'] = []
                        else:
                            if not build_dict['unit_dict_list']:
                                return False, "unit_dict_list can not empty while level is 5"
                            if not isinstance(build_dict['unit_dict_list'], list):
                                return False, "unit_dict_list can only be list"
                            if len(build_dict['unit_dict_list']) > 10:
                                return False, "the length of unit_dict_list can not great than 10"
                            for unit_dict in build_dict['unit_dict_list']:
                                if not isinstance(unit_dict, dict):
                                    return False, "the member of unit_dict_list can only be dict"
                                if unit_dict.keys() != set(['unit', 'project_group_build_unit_id', 'password_num']):
                                    return False, "unit_dict_list only have keys unit, project_group_build_unit_id, password_num"
    return True, ""


def validate_position_level(level):
    if not level:
        return False, "level can not be empty"
    level = str(level)
    if level not in ['2', '3', '4', '5']:
        return False, "level can only be 2 or 3 or 4 or 5"
    return True, ""


def validate_gate_info(gate_info):
    if not isinstance(gate_info, dict):
        return False, "gate_info must be dict"
    if gate_info.keys() != set(['direction', 'gate_name']):
        return False, "gate_info can only have keys direction and gate_name"
    if gate_info['direction'] not in ['I', 'O']:
        return False, "direction can only be I or O"
    return True, ""


def validate_gate_name(gate_name):
    if not gate_name:
        return False, "gate_name can not empty"
    if len(gate_name) > 20:
        return False, "gate_name illegal, only can be a string of not more than 20 characters"
    if not isinstance(gate_name, str):
        return False, "gate_name must str"
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


def validate_bluetooth_rssi(bluetooth_rssi):
    if not bluetooth_rssi:
        return False, "bluetooth_rssi can not be empty"
    bluetooth_rssi = str(bluetooth_rssi)
    bluetooth_rssi_re = re.compile("^-[1-9]+")
    if not bluetooth_rssi_re.match(bluetooth_rssi):
        return False, "bluetooth_rssi must be negative number"
    return True, ""


def validate_wifi_rssi(wifi_rssi):
    if not wifi_rssi:
        return False, "wifi_rssi can not be empty"
    wifi_rssi = str(wifi_rssi)
    wifi_rssi_re = re.compile("^-[1-9]+")
    if not wifi_rssi_re.match(wifi_rssi):
        return False, "wifi_rssi must be negative number"
    return True, ""


def validate_open_time(open_time):
    if not open_time:
        return False, "open_time can not be empty"
    open_time = str(open_time)
    open_time_re = re.compile("^[1-9]+")
    if not open_time_re.match(open_time):
        return False, "open_time can only be number"
    return True, ""


def validate_outer_app_user_id(outer_app_user_id):
    if not outer_app_user_id:
        return False, "outer app user id can not be empty"
    outer_app_user_id = str(outer_app_user_id)
    app_user_id_re = re.compile("^[0-9a-fA-F]{1,32}$")
    if not app_user_id_re.match(outer_app_user_id):
        return False, "outer_app_user_id can only be 1-32 digits"
    return True, ""


def validate_app_user_id(app_user_id):
    return validate_no(app_user_id, "app_user_id")


def validate_server_id(server_id):
    server_id_re = re.compile("^[0-9]{1,6}$")
    if not server_id_re.match(server_id):
        return False, "server_id can only be 6 digits"
    return True, ""


def validate_visitor_app_user_id(app_user_id):
    app_user_id_list = app_user_id.split("@")
    if len(app_user_id_list) not in [1, 3]:
        return False, "visitor_app_user_id must contain 2 @"
    str_day_re = re.compile("^[1-9][0-9]{7}$")
    if not str_day_re.match(str(app_user_id_list[0])):
        return False, "str_day must be 8 digits"
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


def validate_clear_list_dict(clear_list_dict):
    if not isinstance(clear_list_dict, dict):
        return False, "the member of clear_list must dict"
    if clear_list_dict.keys() != set(['black_card_no_list', 'white_card_no_list', 'mac']):
        return False, "the member of clear_list can only have keys black_card_no_list and mac and white_card_no_list"
    if not isinstance(clear_list_dict['black_card_no_list'], list) or not isinstance(
            clear_list_dict['white_card_no_list'], list):
        return False, "black_card_no_list and white_card_no_list must be list"
    mac_flag, mac_str = validate_mac(str(clear_list_dict['mac']))
    if not mac_flag:
        return mac_flag, mac_str
    if len(clear_list_dict['black_card_no_list']) > 100 or len(clear_list_dict['white_card_no_list']) > 100:
        return False, "the length of black_card_no_list and white_card_no_list must within 100"
    clear_list_dict['card_no_list'] = clear_list_dict['black_card_no_list'] + clear_list_dict['white_card_no_list']
    for enc_card_no in clear_list_dict['card_no_list']:
        enc_card_no_check_flag, enc_card_no_check_str = validate_enc_card_no(str(enc_card_no))
        if not enc_card_no_check_flag:
            return enc_card_no_check_flag, enc_card_no_check_str
    return True, ""


def validate_now(timestamp):
    if int(timestamp) < int(time.time()):
        return False, "请选择比当前时间晚的日期"
    return True, ""


def validate_card_no(card_no):
    if not card_no: return False, "card_no can not empty"
    card_no_flag, card_no_str = validate_no(card_no, "card_no", 1, 100)
    if not card_no_flag: return card_no_flag, card_no_str
    return True, ''


def validate_card_sn(card_sn):
    if not card_sn:
        return False, "card_sn can not empty"
    return True, ''


def validate_enc_card_no(enc_card_no):
    return validate_no(enc_card_no, 'card_no')


def validate_card_write_no_list(card_write_no_list):
    if not isinstance(card_write_no_list, list):
        return False, "card_write_no_list must be list"
    for card_write_no in card_write_no_list:
        validate_flag, validate_str = validate_no(str(card_write_no), 'card_write_no')
        if not validate_flag:
            break
    return validate_flag, validate_str


def validate_card_type(card_type):
    if card_type not in ['1', '2', '3', '4', '5']:
        return False, 'card_type can only be 1 or 2 or 3 or 4 or 5'
    return True, ''


def validate_card_validity(card_validity):
    if not card_validity: card_validity = 4294967295
    card_validity_check_flag, card_validity_check_str = validate_timestamp(str(card_validity), 'card_validity')
    if not card_validity_check_flag: return card_validity_check_flag, card_validity_check_str

    now_flag, now_str = validate_now(card_validity)
    if not now_flag: return now_flag, now_str

    return int(card_validity), ''


def validate_card_info(card_info):
    if not isinstance(card_info, dict): return False, "card_info must be dict"

    if card_info.keys() != set(['enc_card_no', 'enc_card_no_count', 'card_no', 'card_type', 'card_validity']):
        return False, "card_info keys can only be 'enc_card_no', 'enc_card_no_count', 'card_no','card_type','card_validity'"

    card_no_check_flag, card_no_check_str = validate_card_no(str(card_info['card_no']))
    if not card_no_check_flag: return card_no_check_flag, card_no_check_str

    enc_card_no_check_flag, enc_card_no_check_str = validate_enc_card_no(str(card_info['enc_card_no']))
    if not enc_card_no_check_flag: return enc_card_no_check_flag, enc_card_no_check_str

    card_type_check_flag, card_type_check_str = validate_card_type(str(card_info['card_type']))
    if not card_type_check_flag: return card_type_check_flag, card_type_check_str

    card_info['card_validity'], card_validity_check_str = validate_card_validity(str(card_info['card_validity']))
    if not card_info['card_validity']: return False, card_validity_check_str

    return True, ""


def validate_app_card_info(card_info):
    if not isinstance(card_info, dict): return False, "card_info must be dict"

    if card_info.keys() != set(['card_no', 'card_type', 'card_validity']):
        return False, "card_info keys can only be 'card_no','card_type','card_validity'"

    if not card_info['card_no']: return False, "card_no can not empty"
    # card_no_check_flag, card_no_check_str = validate_card_no(str(card_info['card_no']))
    # if not card_no_check_flag: return card_no_check_flag, card_no_check_str

    if str(card_info['card_type']) != '5': return False, "card_type can only be 5"

    card_info['card_validity'], card_validity_check_str = validate_card_validity(str(card_info['card_validity']))
    if not card_info['card_validity']: return False, card_validity_check_str

    return True, ""


def validate_project_id(project_id):
    return validate_no(project_id, 'project_id')


def validate_group_id(group_id):
    return validate_no(group_id, 'group_id')


def validate_build_id(build_id):
    return validate_no(build_id, 'build_id')


def validate_unit_id(unit_id):
    return validate_no(unit_id, 'unit_id')


def validate_outer_room_id(outer_room_id):
    return validate_no(outer_room_id, 'outer_room_id', 1, 20)


def validate_id_info(id_info, card_type):
    '''
    id_info = {
        "project_id_list":[
            {
                "project_id":123,
                "group_id":456,
                "build_id":789,
                "unit_id":101
            }
        ],
        "room_id_list":["123","456"]
    }
    '''
    if not isinstance(id_info, dict):
        return False, 'id_info must be dict'
    if not id_info.keys() <= set(['project_id_list', 'room_id_list']):
        return False, 'id_info keys must in ["project_id_list", "room_id_list"]'
    if card_type == 5:
        room_id_list = id_info.get('room_id_list')
        if not room_id_list:
            return False, "room_id_list can not be empty when card_type is 5"
        if len(room_id_list) >= 10: return False, "the length of room_id_list can not great than 9"
        for outer_room_id in room_id_list:
            if not outer_room_id:
                return False, "outer room id can not be empty"
            outer_room_id_check_flag, outer_room_id_check_str = validate_outer_room_id(str(outer_room_id))
            if outer_room_id_check_flag:
                return outer_room_id_check_flag, outer_room_id_check_str
        return True, ""
    project_id_list = id_info.get('project_id_list')
    if not project_id_list: return False, "project_id_list must exits when card_type not equal 5"
    if len(project_id_list) >= 10: return False, "the length of room_id_list can not great than 9"
    for project_id_dict in project_id_list:
        if not project_id_dict.keys() <= set(['project_id', 'group_id', 'build_id', 'unit_id']):
            return False, "project_id_dict keys must in ['project_id', 'group_id', 'build_id', 'unit_id']"
        project_id = project_id_dict.get('project_id')
        if not project_id:
            return False, 'project_id must exists'
        check_project_id_flag, check_project_id_str = validate_project_id(str(project_id))
        if not check_project_id_flag:
            return check_project_id_flag, check_project_id_str
        if card_type == 1:
            continue
        group_id = project_id_dict.get('group_id')
        if not group_id:
            return False, "group_id must exists when card_type in [2,3,4]"
        check_group_id_flag, check_group_id_str = validate_group_id(str(group_id))
        if not check_group_id_flag:
            return check_group_id_flag, check_group_id_str
        if card_type == 2:
            continue
        build_id = project_id_dict.get('build_id')
        if not build_id:
            return False, "build_id must exists when card_type in [3,4]"
        check_build_id_flag, check_build_id_str = validate_build_id(str(build_id))
        if not check_build_id_flag:
            return check_build_id_flag, check_build_id_str
        if card_type == 3:
            continue
        unit_id = project_id_dict.get('unit_id')
        if not unit_id:
            return False, "unit_id must exists when card_type is 4"
        check_unit_id_flag, check_unit_id_str = validate_unit_id(str(unit_id))
        if not check_unit_id_flag:
            return check_unit_id_flag, check_unit_id_str
    return True, ""


def validate_owner_info(owner_info):
    if not isinstance(owner_info, dict):
        return False, "owner_info must be dict"
    if owner_info.keys() != set(['name', 'phone', 'gender', 'gender_str', 'type', 'type_str', 'age',
                                 'age_str', 'role', 'role_str', 'family_structure', 'family_structure_str']):
        return False, "owner_info keys must contain name, phone, gender, type, age, role, family_structure"
    if owner_info['name']:
        name_check_flag, name_check_str = validate_str("resident name", owner_info['name'])
        if not name_check_flag:
            return name_check_flag, name_check_str
    if owner_info['phone']:
        phone_check_flag, phone_check_str = validate_phone(owner_info['phone'])
        if not phone_check_flag:
            return phone_check_flag, phone_check_str
    if owner_info['gender']:
        gender_check_flag, gender_check_str = validate_gender(owner_info['gender'])
        if not gender_check_flag:
            return gender_check_flag, gender_check_str
    return True, ""


def validate_app_owner_info(owner_info):
    if not isinstance(owner_info, dict):
        return False, "owner_info must be dict"
    if owner_info.keys() != set(['name', 'phone']):
        return False, "owner_info keys must contain name, phone"
    if owner_info['name']:
        name_check_flag, name_check_str = validate_str("resident name", owner_info['name'])
        if not name_check_flag:
            return name_check_flag, name_check_str
    if owner_info['phone']:
        phone_check_flag, phone_check_str = validate_phone(owner_info['phone'])
        if not phone_check_flag:
            return phone_check_flag, phone_check_str
    return True, ""


def validate_write_type(write_type):
    if write_type not in ['1', '2']:
        return False, 'write_type can only be 1 ir 2'
    return True, ''


def validate_province(province):
    if province is None:
        return False, "province can not be empty"
    return True, ""


def validate_city(city):
    if city is None:
        return False, "city can not be empty"
    return True, ""


def validate_project(project):
    if project is None:
        return False, "project can not be empty"
    return True, ""


def validate_group(group):
    if group is None:
        return False, "group can not be empty"
    return True, ""


def validate_build(build):
    if build is None:
        return False, "build can not be empty"
    return True, ""


def validate_unit(unit):
    if unit is None:
        return False, "unit can not be empty"
    return True, ""


def validate_status(status):
    if status not in ['0', '1', '2', '3', '4']:
        return False, "status can only 1 or 2 or 3 or 4"
    return True, ""


def validate_outer_project_id(outer_project_id):
    if not outer_project_id:
        return False, "outer project id can not be empty"
    return True, ""


def validate_password(password):
    if not password:
        return False, "密码不能为空"
    password = str(password)
    password_re = re.compile("^\w{4,100}$")
    if not password_re.match(password):
        return False, "密码只能是4-100个字符"
    return True, ""


def validate_list_member_attr(attr_name, attr_value, attr_list):
    if not attr_value:
        return False, "%s can not empty" % attr_name
    if attr_value not in attr_list: return False, "%s can only be in %s" % (attr_name, ','.join(attr_list))
    return True, ""


def validate_area(area, access):
    if not isinstance(area, list):
        return False, "area must be list"
    if len(area) > 1000:
        return False, "the length of area must within 1000"
    if access == 4:
        if area: return False, "area must empty while access is 4"
    return True, ""


def validate_pass_type(pass_type):
    if pass_type not in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
        return False, "pass_type can only be 0 or 1 or 2 or 3"
    return True, ''


def validate_user_pass_list(user_pass_list):
    if not isinstance(user_pass_list, list):
        return False, 'user_pass_list must be list'
    if not user_pass_list:
        return False, 'user_pass_list can not be empty'
    if len(user_pass_list) > 100:
        return False, 'the length of user_pass_list can not great than 100'
    for user_pass in user_pass_list:
        user_pass_flag, user_pass_str = validate_user_pass(user_pass)
        if not user_pass_flag:
            return user_pass_flag, user_pass_str
    return True, ''


def validate_user_pass(user_pass):
    if not isinstance(user_pass, dict):
        return False, 'user_pass can only be dict'
    if not user_pass:
        return False, 'user_pass can not be empty'
    if user_pass.keys() != set(['pass_type', 'created_time', 'mac', 'app_user_id']):
        return False, 'user_pass can only have keys pass_type and created_time and mac and app_user_id'
    pass_type_flag, pass_type_str = validate_pass_type(str(user_pass['pass_type']))
    if not pass_type_flag:
        return pass_type_flag, pass_type_str
    created_time_flag, created_time_str = validate_timestamp(str(user_pass['created_time']), 'created_time')
    if not created_time_flag:
        return created_time_flag, created_time_str
    mac_flag, mac_str = validate_mac(str(user_pass['mac']))
    if not mac_flag:
        return mac_flag, mac_str
    if str(user_pass['pass_type']) in ['0', '1']:
        app_user_id_flag, app_user_id_str = validate_app_user_id(str(user_pass['app_user_id']))
        if not app_user_id_flag:
            return app_user_id_flag, app_user_id_str
    elif str(user_pass['pass_type']) == '2':
        app_user_id_flag, app_user_id_str = validate_server_id(str(user_pass['app_user_id']))
        if not app_user_id_flag:
            return app_user_id_flag, app_user_id_str
    else:
        app_user_id_flag, app_user_id_str = validate_card_no(str(user_pass['app_user_id']))
        if not app_user_id_flag:
            return app_user_id_flag, app_user_id_str
    return True, ""


def validate_heart_time(heart_time):
    if not heart_time:
        return False, 'heart_time can not be empty'
    heart_time_re = re.compile("^\d{1,4}(\.\d{1,2})?$")
    if not heart_time_re.match(heart_time):
        return False, "heart_time can only be positive rational number，1-6 digits"
    return True, ""


def validate_set_app_user_bind_door_method(method):
    if method not in ['set_bind_door_list', 'delete_bind_door_list']:
        return False, "method can only be set_bind_door_list or delete_bind_door_list"
    return True, ""


def validate_server_id(server_id):
    if not server_id:
        return False, "server id can not be empty"
    server_id = str(server_id)
    server_id_length = len(server_id)
    if server_id_length > 6:
        return False, "server id length can not great than 6"
    return server_id.rjust(6, '0'), ""


def validate_brake_type(brake_type):
    if not brake_type:
        return True, ""
    brake_type = str(brake_type)
    if brake_type not in ['1', '2']:
        return False, "brake_type can only be 1 or 2"
    return True, ""


def validate_lately_pass(lately_pass):
    if not lately_pass:
        return True, ""
    lately_pass = str(lately_pass)
    if lately_pass not in ['1', '3', '7', '30']:
        return False, "lately_pass can only be 1,3,7,30"
    return True, ""


def validate_err_log_list(err_log_list):
    if type(err_log_list) not in [str, list]:
        return False, 'err_log_list must be json or list'
    try:
        err_log_list = json.loads(err_log_list) if isinstance(err_log_list, str) else err_log_list
    except ValueError:
        return False, 'err_log_list must be json if err_log_list is str'
    for err_log in err_log_list:
        check_err_log_flag, check_err_log_str = validate_err_log(err_log)
        if not check_err_log_flag:
            return False, check_err_log_str
    return True, ""


def validate_err_log(err_log):
    if not isinstance(err_log, dict):
        return False, "err_log must be dict"
    if err_log.keys() != set(['occur_time', 'brake_mac', 'brake_type', 'phone_info', 'app_user_id', 'reason']):
        return False, 'err_log key error'
    occur_time_flag, occur_time_str = validate_timestamp(err_log['occur_time'], 'occur_time')
    if not occur_time_flag:
        return False, occur_time_str
    return True, ""


def validate_record_list(record_list):
    if type(record_list) not in [str, list]:
        return False, 'record_list must be json or list'
    record_list = json.loads(record_list) if isinstance(record_list, str) else record_list
    if not record_list: return False, "record_list can not empty"
    if len(record_list) > 100: return False, "record list length can not great than 100"
    for record in record_list:
        record_flag, record_str = validate_record(record)
        if not record_flag:
            return False, record_str
    return record_list, ""


def validate_record(record):
    if not isinstance(record, dict):
        return False, 'record must be dict'
    key_list = ['outer_app_user_id', 'machine_mac', 'pass_info', 'pass_time_cost', 'app_device_info']
    if record.keys() > set(key_list):
        return False, 'record keys error'
    return True, ""


def validate_phone_info(phone_info):
    if type(phone_info) not in [str, dict]:
        return False, 'phone_info must be str or dict'
    try:
        phone_info = json.loads(phone_info) if isinstance(phone_info, str) else phone_info
    except ValueError:
        return False, 'phone_info must json if phone_info is str'
    if phone_info.keys() != set(['model', 'os_version']):
        return False, "phone info key error"
    return True, ""


def validate_room_id_list(room_id_list):
    if not room_id_list: return False, "room_id_list can not be empty"
    if not isinstance(room_id_list, list): return False, "room_id_list can only be list"
    if len(room_id_list) >= 10: return False, "the length of room_id_list can not great than 9"

    for room_id in room_id_list:
        room_id_flag, room_id_str = validate_outer_room_id(str(room_id))
        if not room_id_flag: return room_id_flag, room_id_str

    return True, ""


def validate_outer_project_id_list(opil):
    if not opil: return False, None, "outer_project_id_list must be exists"
    opil = json.loads(opil) if isinstance(opil, str) else opil
    if not isinstance(opil, list): return False, None, "outer_project_id_list must be list"
    if len(opil) > 10: return False, None, "不能超过10个项目"
    return True, opil, ""

