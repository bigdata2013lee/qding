# -*- coding: utf-8 -*-
import os
from apps.const import CONST
from apps.basedata.process.sync_bj_data_api import test_get_xml_data


def run():
    xml_dir = CONST['xml_dir']
    xml_dir_list = os.listdir(xml_dir)
    for xml_name in xml_dir_list:
        if xml_name == "bak": continue
        test_get_xml_data(xml_name)
