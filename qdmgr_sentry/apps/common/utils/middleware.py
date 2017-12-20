# -*- coding:utf-8 -*-

from django.http import HttpResponse
import sys
import logging
import traceback
import json
from apps.common.utils.serializer import encode
logger = logging.getLogger('qding')


class SetRemoteAddrFromForwardedFor(object):
    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            pass
        else:
            real_ip = real_ip.split(",")[0]
            request.META['REMOTE_ADDR'] = real_ip


class ExceptionMiddleware(object):
    def process_request(self, request):
        pass

    def process_exception(self, request, exception):
        logger.debug('########## Catch Request Exception ##########')
        result = {'err': 0, 'data': {}, 'msg': '', 'log': ''}
        try:
            raise exception
        except Exception as e:
            sys.stdout.flush()
            result['err'] = 1
            result['msg'] = e
            result['log'] = traceback.format_exc()
            logger.debug('--- request ')
            logger.debug(request)
            logger.debug('--- result')
            logger.debug(result)
            return HttpResponse(json.dumps(encode(result), ensure_ascii=False))
