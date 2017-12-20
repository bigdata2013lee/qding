# --*-- coding:utf8 --*--
from apps.const import CONST
import ctypes


def qall_hash(input_msg, out_bit_len, count=0):
    if not input_msg:
        return None
    if int(out_bit_len) <= 0:
        return None
    libfunc = ctypes.CDLL(CONST['libmeshsubV3_dir'])
    input_buffer = ctypes.create_string_buffer(input_msg.encode("utf8"))
    out_Byte_len = int(out_bit_len / 8) + 1
    output_buffer = (ctypes.c_char * out_Byte_len)()
    libfunc.qall_hash(input_buffer, len(input_msg) + 1, output_buffer, out_bit_len, count)
    out_value = output_buffer.value
    i = 0
    out_count = 0
    for out in out_value:
        out_mem = int(format(out, '02x'), 16)
        out_count += (out_mem * (1 << (i * 8)))
        i += 1
    return out_count


def create_password(project_unit_count, locality, door, start_time, valid_num, count, valid_day):
    libfunc = ctypes.CDLL(CONST['libmeshsubV2_dir'])
    libfunc.mesh_preset(project_unit_count, 100, 100, 0, 1)  # 设定有效密码池
    locality = ctypes.create_string_buffer(locality.encode('utf8'))
    door = ctypes.create_string_buffer(door.encode('utf8'))
    start_time = ctypes.create_string_buffer(start_time.encode('utf8'))
    password = str(libfunc.mesh_generate(locality, door, start_time, valid_day, valid_num, count, 0x12345678))
    black_list = [000000, 111111, 222222, 333333, 444444, 555555, 666666, 777777, 888888, 999999, 123456,
                  654321, 456789, 987654, 147258, 258369, 963852, 963258, 258147, 258741, 789456, 789654,
                  456123, 456321]
    get_count = 0
    while password in black_list:
        count += 1
        get_count += 1
        password = str(libfunc.mesh_generate(locality, door, start_time, valid_day, valid_num, count, 0x12345678))
        if get_count > 10: raise Exception("计算密码超过10次")
    password = password.rjust(6, '0')
    return password


def create_password_1(unit_id, start_time, valid_num, count):
    libfunc = ctypes.CDLL(CONST['libmeshsubV3_dir'])
    input_msg_str = "%s%s" % (str(unit_id), str(start_time))
    input_msg = ctypes.create_string_buffer(input_msg_str.encode("utf8"))
    password = str(libfunc.mesh_generate2(input_msg, len(input_msg_str), valid_num, count, 0x12345678))
    black_list = [000000, 111111, 222222, 333333, 444444, 555555, 666666, 777777, 888888, 999999, 123456,
                  654321, 456789, 987654, 147258, 258369, 963852, 963258, 258147, 258741, 789456, 789654,
                  456123, 456321]
    get_count = 0
    while password in black_list:
        count += 1
        get_count += 1
        password = str(libfunc.mesh_generate2(input_msg, len(input_msg_str), valid_num, count, 0x12345678))
        if get_count > 10: raise Exception("计算密码超过10次")
    password = password.rjust(6, '0')
    return password


def set_basedata_id(input_msg, check_basedata_exists):
    count = 0
    basedata_id = qall_hash(input_msg=input_msg, out_bit_len=32, count=count)
    if basedata_id is None:
        raise Exception('can not get basedata id')
    while not basedata_id or check_basedata_exists(basedata_id):
        count += 1
        basedata_id = qall_hash(input_msg=input_msg, out_bit_len=32, count=count)
        if count > 100: raise Exception("超过100次")
    return basedata_id, count


def set_card_write_no(write_list, card_no, count, version_num=2):
    pre_write_no = (ctypes.c_uint * 11)(0xff)
    for i in range(len(write_list)):
        pre_write_no[i] = write_list[i]

    pre_card_no = ctypes.c_uint(card_no)
    card_no_pt = ctypes.pointer(pre_card_no)
    card_no_len = 4

    write_no_pt = ctypes.pointer(pre_write_no)
    write_no_len = 4 * 11

    lib_func = ctypes.CDLL(CONST['libmeshsubV3_dir'])
    ret = lib_func.iccard_encrypt(card_no_pt, card_no_len, write_no_pt, write_no_len)

    if ret == 0:
        return 0
    ret_str = "%s%s%s" % (format(ret, '04x'), format(count, '02x'), format(version_num, '02x'))
    for j in range(11):
        ret_str = "%s%s" % (ret_str, format(write_no_pt.contents[j], '08x'))
    return ret_str
