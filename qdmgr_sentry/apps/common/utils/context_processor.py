# -*- coding: utf-8 -*-

from django.conf import settings


def AddConstContext(request):
    return {'CONST': settings.CONST}
