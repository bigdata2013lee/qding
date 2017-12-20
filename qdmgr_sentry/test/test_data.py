# --*-- coding:utf8 --*--
import json
from apps.basedata.classes.Basedata_BJ_App_User import Basedata_BJ_App_User
from apps.basedata.classes.Basedata_Apartment import Basedata_Apartment

db_app_user = Basedata_BJ_App_User.objects().first()
if db_app_user:
    app_user = json.loads(db_app_user.to_json())
else:
    app_user = {
        "id": "57ccdcf6cdc8720bc55b2971",
        "phone": "12345678901",
        "outer_app_user_id": "8aa57dca4fcfaf9f01508423b56c0109",
        "app_user_id": 3900903306,
    }

db_apartment = Basedata_Apartment.objects().first()
if db_apartment:
    apartment = json.loads(db_apartment.to_json())
else:
    apartment = {
        "id": "578cf7cacdc8720d236e517d",
        "status": "1",
        "province": "江苏",
        "city": "无锡",
        "project": "紫云台",
        "group": "紫云台一期一组团别墅",
        "build": "89-95",
        "unit": "1",
        "room": "89",
        "outer_city_id": "2",
        "outer_project_id": "105",
        "outer_group_id": "1",
        "outer_build_id": "72509",
        "outer_room_id": "632374",
        "project_id": 160545703,
        "group_id": 3519368584,
        "build_id": 468017329,
        "unit_id": 2720515946,
    }

brake_machine = {
    "id": "57c4f744cdc8721e6a796855",
    "status": "1",
    "position": {
        "project_list": [
            {
                "project": "紫云台",
                "group_list": []
            }
        ],
        "level": 2,
        "city": "无锡",
        "province": "江苏"
    },
    "gate_info": {
        "gate_name": "test门",
        "direction": "I"
    },
    "mac": "112233445566",
    "command": "0",
    "open_time": "5",
    "bluetooth_rssi": "-76",
    "wifi_rssi": "-76",
    "version": "57c4f603cdc8721cc4439a3d",
    "heart_time": 24,
    "is_monit": 0
}

web_user = {
    "id": "578cf895cdc8720d33079372",
    "status": "1",
    "user_type": 20,
    "username": "千丁管理员",
    "password": "195d15abf53cadb251bc7231ba1342be",
    "brake_config_password_num": 0,
    "project_list": [
        "578cf7c8cdc8720d236e5137",
        "5791e983cdc872298c73f51d",
        "579797a6cdc872091134a37a",
        "579797accdc872091134a37b",
        "579797b1cdc872091134a37d",
        "579797bdcdc872091134a380",
        "579cdafdcdc8722e7c5ea193",
        "579cdb00cdc8722e7c5ea1be",
        "579cdb0acdc8722e7c5ea1d3",
        "579cdb0fcdc8722e7c5ea223",
        "57a0e43bcdc8720a547e707d",
        "57b47e75cdc87219b2d02152",
        "57b47ecdcdc87219b2d024fd",
        "57c40275cdc87210bc370787",
    ],
    "brake_config_password": "195d15abf53cadb251bc7231ba1342be",
}

brake_card = {
    "id": "57d76089cdc8721beda8246a",
    "status": "1",
    "card_no": 1154369401076865,
    "card_sn": "419e492173c81",
    "enc_card_no": 3433904730,
    "card_type": 5,
    "card_validity": 1476060946,
    "card_owner": {
        "apartment": {
            "province": "江苏",
            "city": "无锡",
            "project": "紫云台",
            "group": "紫云台一期一组团别墅",
            "build": "89-95",
            "unit": "1",
            "room": "89",
            "project_id": 160545703,
            "group_id": 3519368584,
            "build_id": 72509,
            "unit_id": 2720515946,
            "outer_project_id": "105",
            "outer_group_id": "1",
            "outer_build_id": "72509",
            "outer_room_id": "632374",
        },
        "phone": "18188621491",
        "gender": "M",
        "name": "julian"
    },
    "card_area": [
        {
            "province": "江苏",
            "city": "无锡",
            "project": "紫云台",
            "group": "紫云台一期一组团别墅",
            "build": "89-95",
            "unit": "1",
            "room": "89",
            "outer_project_id": "105",
            "outer_group_id": "1",
            "outer_build_id": "72509",
            "outer_room_id": "632374",
            "project_id": 160545703,
            "build_id": 72509,
            "unit_id": 2720515946,
            "group_id": 3519368584
        }
    ],
}

brake_config_version = {
    "id": "57faeaeacdc87221468e3abd",
    "status": "1",
    "version": "V1.2",
    "former_version": "V1.1",
    "file_uri": "http://www.qding.cloud/uploads/brake_config/apk/test.tt",
    "md5sum": "5555",
    "message": "test.55"
}

brake_version = {
    "id": "57978a8ccdc8721bf5a3f6f1",
    "status": "2",
    "version": "V1.1",
    "former_version": "",
    "file_uri": "http://www.qding.cloud/uploads/brake/rom/test.test",
    "md5sum": "test_md5",
    "message": "test brake",
}

config_user = {
    "id": "578cf895cdc8720d33079374",
    "status": "1",
    "user_type": 40,
    "phone": "12345678901",
    "brake_config_password": "e10adc3949ba59abbe56e057f20f883e",
    "brake_config_password_num": 0,
    "project_list": [
        "578cf7c8cdc8720d236e5137",
        "5791e983cdc872298c73f51d",
        "579797a6cdc872091134a37a",
        "579797accdc872091134a37b",
        "579797b1cdc872091134a37d",
        "579797bdcdc872091134a380",
        "579cdafdcdc8722e7c5ea193",
        "579cdb00cdc8722e7c5ea1be",
        "579cdb0acdc8722e7c5ea1d3",
        "579cdb0fcdc8722e7c5ea223",
        "57a0e43bcdc8720a547e707d",
        "57b47e75cdc87219b2d02152",
        "57b47ecdcdc87219b2d024fd",
        "57c40275cdc87210bc370787",
    ]
}
