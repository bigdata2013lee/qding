#coding=utf8
import json
import logging
import os
from apis.base import BaseApi
from conf.qd_conf import CONF
from utils.tools import get_default_result

log = logging.getLogger('django')

class JsonApi(BaseApi):

    def get_json(self, filename=""):
        """
        提供给前端Web开发时，通过json文件模拟Api接口数据
        """
        result = get_default_result()
        data = b''
        with open(os.path.join(CONF.get("app_home"), "src/web/static/testjsons/%s.json" % filename), "rb") as json_file:
            data = json_file.read()

        if not data:
            return result.setmsg("not found json file", 3)

        try:
            result = json.loads(data.decode("utf-8"))
        except Exception as e:
            result.setmsg("json format error", 3)

        return result

    def test1(self):
        result = get_default_result()
        return result

