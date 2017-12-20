# --*-- coding:utf8 --*--
from settings.const import CONST
from apps.const import CONST as app_const
from urllib import request
import re, os, shutil
import logging

logger = logging.getLogger('qding')


def down_html_page(url=CONST['bj_data_url']['url']):
    try:
        response = request.urlopen(url)
        code = response.getcode()
        if code != 200:
            return None
        page = response.read()
        response.close()
        return page.decode('utf8')
    except Exception as e:
        logger.exception("exception:%s" % e)
        return None


def get_xml_file_name_list(page):
    try:
        if not page: return []
        xml_file_name_list = []
        page_re = re.compile('[0-9]+\.xml')
        tmp_list = page_re.findall(page)
        for x in tmp_list:
            if x not in xml_file_name_list:
                xml_file_name_list.append(x)
        return xml_file_name_list
    except Exception as e:
        logger.exception("exception:%s" % e)
        return []


def clean_up_xml_dir(dir=app_const['xml_dir']):
    try:
        tmp_file_list = os.listdir(dir)
        bak_dir = "%sbak" % dir
        if os.path.exists(bak_dir): shutil.rmtree(bak_dir)
        os.mkdir(bak_dir)
    except Exception as e:
        logger.exception("exception:%s" % e)
        tmp_file_list = []
    for tmp_file in tmp_file_list:
        try:
            src_file_dir = "%s%s" % (dir, tmp_file)
            if os.path.isdir(src_file_dir):
                continue
            shutil.move(src_file_dir, bak_dir)
        except Exception as e:
            logger.exception("exception:%s" % e)


def down_xml(xml_file_name_list, url=CONST['bj_data_url']['url'], dir=app_const['xml_dir']):
    for xml_file in xml_file_name_list:
        try:
            xml_url = "%s%s" % (url, xml_file)
            xml_dir = "%s%s" % (dir, xml_file)
            request.urlretrieve(xml_url, xml_dir)
            return True
        except Exception as e:
            logger.exception("exception:%s" % e)
            return False
