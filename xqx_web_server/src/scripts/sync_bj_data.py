# --*-- coding:utf8 --*--
from apis.outer.sync_bj_data import get_xml_data


def run(project_id):
    xml_file = "%s.xml" % project_id
    get_xml_data(xml_file)
