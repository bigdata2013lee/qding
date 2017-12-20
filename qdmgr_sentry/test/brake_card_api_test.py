# --*-- coding:utf8 --*--
from apps.common.api.brake_api import Brake_Card_Api
from test.test_data import brake_card, app_user

card_info = {
    "card_no": brake_card['card_no'],
    "enc_card_no": 0,
    "enc_card_no_count": 0,
    "card_type": 5,
    "card_validity": 1234567890,
}
id_info = {
    "project_id_list": [
        {
            "project_id": brake_card['card_owner']['apartment']['project_id'],
            "group_id": brake_card['card_owner']['apartment']['group_id'],
            "build_id": brake_card['card_owner']['apartment']['build_id'],
            "unit_id": brake_card['card_owner']['apartment']['unit_id']
        }
    ],
    "room_id_list": [brake_card['card_owner']['apartment']['outer_room_id']]
}
owner_info = {
    "name": brake_card['card_owner']['name'],
    "gender": brake_card['card_owner']['gender'],
    "phone": brake_card['card_owner']['phone'],
}


def test_brake_card_api():
    result = test_read_card()
    test_get_write_no(result)
    test_open_card()
    test_delete_card()
    test_get_black_and_white_list()
    test_clear_or_add_open_door_list()
    test_get_card_by_filter()
    test_modify_card()


def test_read_card():
    params = {"card_no": brake_card['card_no'], "card_sn": brake_card['card_sn']}
    return Brake_Card_Api().read_card(**params)


def test_get_write_no(result={}):
    enc_card_no = result['data']['enc_card_no']
    enc_card_no_count = result['data']['count']
    card_info.update({
        "enc_card_no": enc_card_no,
        "enc_card_no_count": enc_card_no_count,
    })
    params = {"card_info": card_info, "id_info": id_info}
    Brake_Card_Api().get_write_no(**params)


def test_open_card():
    params = {"card_info": card_info, "id_info": id_info, "owner_info": owner_info}
    Brake_Card_Api().open_card(**params)


def test_delete_card():
    params = {"card_no": brake_card['card_no']}
    Brake_Card_Api().delete_card(**params)


def test_get_black_and_white_list():
    params = {"outer_app_user_id": app_user['outer_app_user_id']}
    Brake_Card_Api().get_black_and_white_list(**params)


def test_clear_or_add_open_door_list():
    params = {"operate_list": []}
    Brake_Card_Api().clear_or_add_open_door_list(**params)


def test_get_card_by_filter():
    params = {}
    Brake_Card_Api().get_card_by_filter(**params)


def test_modify_card():
    params = {}
    Brake_Card_Api().modify_card(**params)
