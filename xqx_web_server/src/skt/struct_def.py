#coding=utf-8
import os
from collections import namedtuple
import struct
import re
import ctypes

import logging
log = logging.getLogger("skt")
"""
logging.basicConfig(level=logging.DEBUG)
log = logging
"""

pwd = os.path.abspath(os.path.dirname(__file__))
data_struct_types = {}  # 把定义的结构放入dict,通过type来取


def make_namedtuple(typename, field_names, cfmt, ctype=0,bytes_fields=[]):
    DataTuple = namedtuple(typename, field_names)
    DataTuple._cfmt = cfmt
    DataTuple._ctype = ctype
    DataTuple._typename = typename

    data_struct_types[ctype] = DataTuple

    def _make_from_pack(data):
        """
        bytes 转 namedtuple
        :param data:
        :return:
        """
        _data = data[:struct.calcsize(DataTuple._cfmt)]
        t = DataTuple._make(struct.unpack(DataTuple._cfmt, _data))

        if not re.findall("s", DataTuple._cfmt):
            return t

        fmt_find = re.findall("((?:\d+)?\w)", DataTuple._cfmt)
        _index = -1
        for ff in fmt_find:
            _index += 1
            if not "s" in ff: continue
            _field_name = DataTuple._fields[_index]
            if _field_name in bytes_fields: continue
            new_fv = {_field_name: t[_index].decode("utf-8").replace("\x00", "")}
            t = t._replace(**new_fv)

        return t

    def _parse2bytes(nt):
        """
        namedtuple 转 bytes
        :param nt:
        :return:
        """
        values = []
        for d in nt:
            if isinstance(d, str):
                d = d.encode('utf-8')

            values.append(d)

        _bytes = struct.pack(DataTuple._cfmt, *values)
        return _bytes

    def _struct_calcsize():

        return struct.calcsize(cfmt)

    DataTuple.make_from_pack = _make_from_pack
    DataTuple.calcsize = _struct_calcsize
    DataTuple.parse2bytes = _parse2bytes

    return DataTuple


class DataParser(object):
    DATA_HEAD_FG = 0x5A5AA5A5
    ROINFO = b'\x5A\xA0\x52\x3B\xD6\xB3\x29\xE3'
    libmeshsub = ctypes.cdll.LoadLibrary(pwd + '/libmeshsub.so')

    @classmethod
    def parse(cls, data):
        """把bytes转为可视数据"""
        log.debug("=======Start 数据解析=======")
        max_len = 1024
        parse_result = dict(err=0, payload_list=[])
        if not 12 <= len(data) <= max_len:
            parse_result['err'] = 1
            return parse_result

        packet_head = PacketHead.make_from_pack(data)
        log.debug(packet_head)

        data = data[PacketHead.calcsize():]
        parse_result['packet_head'] = packet_head
        parse_result['payload_list'] = []

        if packet_head.head not in [cls.DATA_HEAD_FG]:
            parse_result['err'] = 2
            return parse_result

        # 解密数据
        if not cls._decrypt(data, packet_head.chksum):
            parse_result['err'] = 3
            return parse_result

        while data:
            if len(data) < 1: break
            data_item_head = DataItemHead.make_from_pack(data)
            log.debug(data_item_head)

            data = data[DataItemHead.calcsize():]

            if len(data) < 1: break
            DATA_STRUCT = data_struct_types.get(data_item_head.type)
            payload = DATA_STRUCT.make_from_pack(data)
            log.debug(payload)

            data = data[DATA_STRUCT.calcsize():]
            parse_result['payload_list'].append(payload)

        log.debug("%d length remaining", len(data))
        log.debug("=======End 数据解析=======")
        return parse_result

    @classmethod
    def parse2bytes(cls, topic, payloads=[], ex_bytes=b''):
        """把数据转为bytes"""
        payload_bytes = b''
        log.debug("=======Start 数据打包=========")
        for payload in payloads:
            _bytes = payload.parse2bytes()
            data_item_head = DataItemHead._make([payload._ctype, 2, len(_bytes)])
            _dih_bytes = data_item_head.parse2bytes()
            log.debug(data_item_head)
            log.debug(payload)
            payload_bytes += _dih_bytes
            payload_bytes += _bytes

        payload_bytes += ex_bytes
        
        enc = cls._encrypt(payload_bytes) #enc=chksum

        #len = payload + packet_head
        pack_head = PacketHead._make([cls.DATA_HEAD_FG, len(payload_bytes) + PacketHead.calcsize(), enc, topic, 1])
        log.debug(pack_head)

        head_bytes = pack_head.parse2bytes()
        transfer_bytes = head_bytes + payload_bytes
        log.debug("=======End 数据打包=========")
        return transfer_bytes

    @classmethod
    def _encrypt(cls, data):
        """加密"""
        enc = cls.libmeshsub.iccard_encrypt(cls.ROINFO, len(cls.ROINFO), data, len(data))
        return enc

    @classmethod
    def _decrypt(cls, data, enc):
        """解密"""
        flg = cls.libmeshsub.iccard_decrypt(cls.ROINFO, len(cls.ROINFO), data, len(data), enc)
        if not flg:
            log.warning("Decrypt data fail.")

        return flg


PacketHead = make_namedtuple("PacketHead", "head,len,chksum,topic,net", "=lHHbb")
DataItemHead = make_namedtuple("DataItemHead", "type,direction,len", "=bbH")

# 防区
PayloadFangQu = make_namedtuple("PayloadFangQu", "fq_id,fq_type,addr,trigger_state", "=bbbb", 9)

# 布防状态
PayloadBuFang = make_namedtuple("PayloadBuFang", "fq_id,enable,trigger_delay,enable_delay", "=bbHH", 4)

#报警
PayloadAlarm = make_namedtuple("PayloadAlarm", "alarm_id,alarm_type", "=bb", 5)

#设备基本信息
PayloadDevInfo = make_namedtuple("PayloadDevInfo", "uid,room,mac,sw_version,hw_version,res_version", "=24s32s24s8s8s8s", 6)

PayloadFileInfo = make_namedtuple("PayloadFileInfo", "fi_id,fi_type,fi_size,chksum,version", "=32sbHH8s", 7)

# 请求数据段
PayloadDataSectionReq = make_namedtuple("PayloadDataSectionReq", "fi_id,offset", "=32sH", 12)

# 下载数据段
PayloadDataSection = make_namedtuple("PayloadDataSection", "fi_id,fi_size,data_size,data_chksum,range_length,data", "=32sHHHH512s", 13, bytes_fields=['data'])

# 版本升级
PayloadVerInof = make_namedtuple("PayloadVerInof", "type,version,host,port", "=b8s32sH", 14)


if __name__ == "__main__":
    bb = b'\xa5\xa5ZZ\xa7\x00\x1b\x92\n\x01D\':\xcfo\x87a\xf9Kq`\xf9\xa6\xedg\xf7\x9b\\e\xf8\xf9\xcff\xae\xd4\xa1a\xf6\xca\x1b`\xfc/\xd50\xadQ*o\xfa5\xbfg\xa9R^h\xae\xe5\xc8i\xfd\xa1\x90Y\xcf\xbc"Z\xcf\xef\xd7`\xf7\xca|k\xfe7\xe9k\xf5\x18Yf\xfcp\xfd\\\xcf^\x8f]\xcfH\x0fm\xe1\xa1\xb3^\xcf\x9fE_\xcf\xca\xd7_\xcf\xd4GP\xe11\xfc`\xcf\x15\x8fL\xcf5\x11L\xfb\x7f\x85b\xcflDc\xcf\x87\xd6c\xcf\xa2hd\xcf\xbd\xfad\xcf\xd8\x8ce\xcf\xf3\x1ef\xcf\x0e\xb1f\xcf)Cg\xcfD\xd5g\xcf_'

    res = DataParser.parse(bb)

    print(res)