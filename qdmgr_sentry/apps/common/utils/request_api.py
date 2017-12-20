# -*- coding: utf-8 -*-
import logging
import json
import requests
from settings.const import CONST
session = requests.Session()
logger = logging.getLogger('qding')


def request_bj_server(method_url, data_key=None, method_params={}, post_flag=True,
                      domain_root = CONST['bj_api_url']['api_url'], timeout=30):
    url = "%s%s" % (domain_root, method_url)
    response = None
    try:
        if post_flag:
            response = session.post(url, data=method_params, timeout=timeout).content.decode('utf8')
        else:
            response = session.get(url, timeout=timeout).content.decode('utf8')
        if not response:
            return None
        response_dict = json.loads(response)
        if not response_dict:
            return None
        if not isinstance(response_dict, dict):
            return None
        response_dic_data = response_dict.get("data", None) or None
        if not data_key:
            return response_dic_data
        else:
            return response_dic_data.get(data_key, None) or None
    except Exception as e:
        logger.debug("%s %s %s" % (url, response, e))
        return None
