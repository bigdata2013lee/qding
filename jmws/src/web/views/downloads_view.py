# coding=utf8
import base64
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.shortcuts import render



log = logging.getLogger('django')


def _download_chunks(file_data=b'', buf_size=512):
    offset, file_size = 0, len(file_data)
    while offset < file_size:
        yield file_data[offset:offset + buf_size]
        offset += buf_size



def speek(request):

    """
    App ID: 9874053
    API Key: usKRwQp7HTi7u6LdVzUL6DNx
    Secret Key: 3756623f3def4eb63ccf4f376f863038
    """

    from aip import AipSpeech
    from utils import tools

    APP_ID = '9874053'
    API_KEY = 'usKRwQp7HTi7u6LdVzUL6DNx'
    SECRET_KEY = '3756623f3def4eb63ccf4f376f863038'

    speek_txt = request.REQUEST.get("speek_txt", "")
    aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    result = aipSpeech.synthesis(speek_txt, 'zh', 1, {'vol': 8})

    if isinstance(result, dict):
        raise Http404

    response = StreamingHttpResponse(_download_chunks(result))
    response['Content-Length'] = '%d' % len(result)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s.mp3"' % tools.get_uuid()
    return response
