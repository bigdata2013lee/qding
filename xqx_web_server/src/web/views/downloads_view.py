# coding=utf8
import base64
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.shortcuts import render

from models.common import QDVersion

from models.record import CallRecord
from utils.qd import RdsGfsFileCache

log = logging.getLogger('django')


def _download_chunks(file_data=b'', buf_size=1024):
    offset, file_size = 0, len(file_data)
    while offset < file_size:
        yield file_data[offset:offset + buf_size]
        offset += buf_size


def get_upgrade_file(request, ver_id):

    ver = QDVersion.objects(id=ver_id).first()
    if not ver or not ver.bin_file:
        log.warning("Not found version obj")
        raise Http404("Not found the version infos")

    gfs_file = ver.bin_file
    RdsGfsFileCache.set(gfs_file)
    download_chunks = RdsGfsFileCache.get(gfs_file._id)

    response = StreamingHttpResponse(download_chunks)
    response['Content-Length'] = '%d' % gfs_file.length
    response['Content-Type'] = gfs_file.content_type or 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % gfs_file.name
    return response


def get_adv_meida_file(request, media_file_id):
    """
    下载广告媒体文件
    :param request:
    :param media_file_id:
    :return:
    """
    from bson.objectid import ObjectId
    from models.common import AdvMedia

    adv = AdvMedia.objects(media_file=ObjectId(media_file_id)).first()
    if not adv or not adv.media_file:
        log.warning("Not found AdvMeida obj or media file")
        raise Http404("Not found AdvMeida obj or media file")

    RdsGfsFileCache.set(adv.media_file)
    download_chunks = RdsGfsFileCache.get(adv.media_file._id)

    response = StreamingHttpResponse(download_chunks)
    response['Content-Length'] = '%d' % adv.media_file.length
    response['Content-Type'] = adv.media_file.content_type or 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % adv.media_file.name
    return response


def get_image_app_avatar(request, user_id):
    from models.aptm import Room, Project  # 不能删
    from models.account import QdUser
    from apis.outer.bjqd import BjQdingApi

    user = QdUser.objects(id=user_id).first()
    if not user:
        raise Http404("Not found the user")

    log.debug(user.domain)
    if user.domain == 'www.qdingnet.com':
        avatar_url = BjQdingApi._get_user_avatar_url(user.source_data_info.get("outer_id", ""))
        log.debug(avatar_url)
        return HttpResponseRedirect(avatar_url)

    if user.domain == "sz.qdingnet.com" and not user.avatar:
        raise Http404("Not found the user avatar")

    avatar = user.avatar
    img = base64.standard_b64decode(avatar.base64)

    response = StreamingHttpResponse(_download_chunks(img))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Length'] = '%d' % len(img)
    response['Content-Disposition'] = 'attachment;filename="%s.jpg"' % user_id

    return response


def get_call_index_snapshot(request, call_id):
    call = CallRecord.objects(id=call_id).first()
    if not (call and call.index_snapshot):
        raise Http404("Not found the call or index_snapshot")

    snapshot = call.index_snapshot
    img = base64.standard_b64decode(snapshot.base64)

    response = StreamingHttpResponse(_download_chunks(img))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Length'] = '%d' % len(img)
    response['Content-Disposition'] = 'attachment;filename="%s.jpg"' % call_id

    return response






