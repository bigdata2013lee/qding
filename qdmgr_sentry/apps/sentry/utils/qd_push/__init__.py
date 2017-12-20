
# -*- coding: utf-8 -*-

import ctypes
from apps.sentry.utils.xg_push import xinge
from apps.sentry.utils.bd_push import Channel
import os,time
from apps.common.utils.xutil import is_digit
import logging
logger = logging.getLogger('qding')



SERVICE_PROVIDERS = {
    'BD': {
        'type': 0,
        'api_key': 'hWgk7lCY5SGFEEvauGV3cwCv',
        'secret_key': 'h31ihzVjfe7qVEkiD4HjvN1GhgQzgnoq',
    },

    'XG': {
        'type': 1,
        'api_key': 2100096723,
        'secret_key': '8d511a768774c9743e995615224d3aaf',
    },
}

ENCRYPT_KEY = 0x8DF8A035
DLL_PATH = os.path.abspath(os.path.dirname(__file__))+os.sep+'libqdkey.so'


def PushMsg(msg, tag):
    ch = Channel.Channel(SERVICE_PROVIDERS['BD']['api_key'], SERVICE_PROVIDERS['BD']['secret_key'])
    cnt=ch.pushMessage(Channel.Channel.PUSH_TO_TAG, msg, str(time.time()), { Channel.Channel.TAG_NAME: tag })
    if not cnt:PushMsg(msg, tag)
    

def mac_to_hash(mac,qr_server_id):
    if mac=='0000':return mac
    mac_str=''
    if not mac or qr_server_id is None:return mac_str
    libfunc=ctypes.CDLL(DLL_PATH)
    p_mac_str=ctypes.create_string_buffer(mac.replace(':','').encode('utf8'),16)
    p_output_mac_str=ctypes.create_string_buffer(8)
    out_len=libfunc.qdhash_str(p_mac_str,p_output_mac_str,int(qr_server_id))
    if out_len !=-1:mac_str=p_output_mac_str[0:4].decode('utf8')
    return mac_str

def pack_message(codeIndex,enc_key):
    encCodeIndex=""
    if not codeIndex or enc_key is None:return encCodeIndex
    try:
        libfunc = ctypes.CDLL(DLL_PATH)
        p_msg_str  = ctypes.create_string_buffer(codeIndex.encode('utf8'))
        p_encry_byte = ctypes.create_string_buffer(1024*16)
        out_len = libfunc.qdmenc_str(p_msg_str,p_encry_byte,1024*16,int(enc_key,16))
    
        if out_len>0:
            encCodeIndex=p_encry_byte[0:out_len].decode('utf8','ignore')
        return encCodeIndex.replace('\x00','')
    except:
        return ""


def unpack_message(encCodeIndex,dec_key):
    decCodeIndex=""
    if not encCodeIndex or not dec_key:return decCodeIndex
    libfunc = ctypes.CDLL(DLL_PATH)
    p_encry_byte = ctypes.create_string_buffer(encCodeIndex.encode('utf8'))
    p_decry_byte = ctypes.create_string_buffer(1024*16)
    out_len = libfunc.qdmdec_hex_str(p_encry_byte,p_decry_byte,1024*16,int(dec_key,16))
    
    if out_len>0:
        decCodeIndex=p_decry_byte[0:out_len].decode('utf8','ignore')
    return decCodeIndex.replace('\x00','')


