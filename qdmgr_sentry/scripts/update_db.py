# --*-- coding:utf8 --*--
from pymongo import MongoClient
import redis
import pickle

'''
connect redis
'''
REDIS = {
    'host': '127.0.0.1',
    'port': '6379',
    'db': 0,
    'password': '',
}
pool = redis.ConnectionPool(host=REDIS['host'], port=REDIS['port'], db=REDIS['db'])
rc = redis.Redis(connection_pool=pool, socket_timeout=20)

'''
connect db
'''
MONGODB = {
    "host": "127.0.0.1",
    "port": 27017,
    "username": "",
    "password": "",
    "db": "qdmgr_sentry",
}

if MONGODB['username'] and MONGODB['password']:
    url = "mongodb://%s:%s@%s:%s" % (MONGODB['username'],
                                     MONGODB['password'],
                                     MONGODB['host'],
                                     MONGODB['port'])
else:
    url = "mongodb://%s:%s" % (MONGODB['host'], MONGODB['port'])

client = MongoClient(url)
db = client[MONGODB['db']]


def get_data(collection_name, document_id):
    key = "update_db_%s" % str(document_id)
    ret = rc.get(key)
    if ret: return pickle.loads(ret)
    collection = getattr(db, collection_name)
    if not collection: return ret
    find_one = getattr(collection, "find_one")
    ret = find_one({"_id": document_id})
    if ret:
        rc.set(key, pickle.dumps(ret))
        rc.expire(key, 3600)
    return ret


'''
start update
'''


def update_sentry_visitor(page_size):
    visitor_list = db.sentry_visitor.find({"_brake_password": None}).limit(page_size)
    visitor_list_count = visitor_list.count()
    while visitor_list_count:
        for visitor in visitor_list:
            _brake_password = {
                "valid_num": 0,
                "password": "",
                "start_time": None,
                "end_time": None,
                "bj_app_user": {
                    "outer_app_user_id": "",
                    "app_user_id": None,
                    "phone": "",
                },
                "apartment": {
                    "province": "",
                    "city": "",
                    "project": "",
                    "group": "",
                    "build": "",
                    "unit": "",
                    "room": "",
                    "outer_project_id": "",
                    "outer_group_id": "",
                    "outer_build_id": "",
                    "outer_room_id": "",
                    "project_id": None,
                    "group_id": None,
                    "build_id": None,
                    "unit_id": None,
                }
            }
            password_id = visitor.get('brake_password', None)
            if password_id:
                brake_password = get_data("brake_password", password_id)
                if brake_password:
                    _brake_password['valid_num'] = brake_password.get('valid_num', 0)
                    _brake_password['password'] = brake_password.get('password', '')
                    _brake_password['start_time'] = brake_password.get('start_time', None)
                    _brake_password['end_time'] = brake_password.get('end_time', None)
                    bj_app_user_id = brake_password.get('bj_app_user', None)
                    if bj_app_user_id:
                        bj_app_user = get_data("basedata_bj_app_user", bj_app_user_id)
                        if bj_app_user:
                            _brake_password['bj_app_user']['outer_app_user_id'] = bj_app_user.get('outer_app_user_id',
                                                                                                  '')
                            _brake_password['bj_app_user']['app_user_id'] = bj_app_user.get('app_user_id', None)
                            _brake_password['bj_app_user']['phone'] = bj_app_user.get('phone', '')
                    apartment_id = brake_password.get('apartment', None)
                    if apartment_id:
                        apartment = get_data("basedata_apartment", apartment_id)
                        if apartment:
                            _brake_password['apartment']['province'] = apartment.get('province', '')
                            _brake_password['apartment']['city'] = apartment.get('city', '')
                            _brake_password['apartment']['project'] = apartment.get('project', '')
                            _brake_password['apartment']['group'] = apartment.get('group', '')
                            _brake_password['apartment']['build'] = apartment.get('build', '')
                            _brake_password['apartment']['unit'] = apartment.get('unit', '')
                            _brake_password['apartment']['room'] = apartment.get('room', '')
                            _brake_password['apartment']['outer_project_id'] = apartment.get('outer_project_id', '')
                            _brake_password['apartment']['outer_group_id'] = apartment.get('outer_group_id', '')
                            _brake_password['apartment']['outer_build_id'] = apartment.get('outer_build_id', '')
                            _brake_password['apartment']['outer_room_id'] = apartment.get('outer_room_id', '')
                            _brake_password['apartment']['project_id'] = apartment.get('project_id', None)
                            _brake_password['apartment']['group_id'] = apartment.get('group_id', None)
                            _brake_password['apartment']['build_id'] = apartment.get('build_id', None)
                            _brake_password['apartment']['unit_id'] = apartment.get('unit_id', None)
            db.sentry_visitor.update({"_id": visitor['_id']}, {"$set": {"_brake_password": _brake_password}})
        print("finish %s sentry_visitor" % visitor_list_count)
        visitor_list = db.sentry_visitor.find({"_brake_password": None}).limit(page_size)
        visitor_list_count = visitor_list.count()


def update_brake_pass(page_size):
    brake_pass_list = db.brake_pass.find({"pass_info": None}).limit(page_size)
    brake_pass_list_count = brake_pass_list.count()
    while brake_pass_list_count:
        for brake_pass in brake_pass_list:
            pass_info = {
                "brake_machine": {
                    "position": {},
                    "gate_info": {},
                    "mac": "",
                },
                "app_user": {
                    "phone": "",
                    "outer_app_user_id": "",
                    "app_user_id": None,
                },
                "brake_password": {
                    "password": "",
                },
                "brake_card": {
                    "card_no": None,
                    "card_owner": {},
                },
            }
            brake_machine_id = brake_pass.get("brake_machine", None)
            if brake_machine_id:
                brake_machine = get_data("brake_machine", brake_machine_id)
                if brake_machine:
                    pass_info['brake_machine'] = {
                        "position": brake_machine.get("position", {}),
                        "gate_info": brake_machine.get("gate_info", {}),
                        "mac": brake_machine.get("mac", ""),
                    }
            app_user_id = brake_pass.get("bj_app_user", None)
            if app_user_id:
                app_user = get_data("basedata_bj_app_user", app_user_id)
                if app_user:
                    pass_info['app_user'] = {
                        "phone": app_user.get("phone", ""),
                        "outer_app_user_id": app_user.get("outer_app_user_id", ""),
                        "app_user_id": app_user.get("app_user_id", None)
                    }
            brake_password_id = brake_pass.get("brake_password", None)
            if brake_password_id:
                brake_password = get_data("brake_password", brake_password_id)
                if brake_password:
                    pass_info['brake_password'] = {
                        "password": brake_password.get("password", "")
                    }
                    app_user_id = brake_password.get("bj_app_user", None)
                    if app_user_id:
                        app_user = get_data("basedata_bj_app_user", app_user_id)
                        if app_user:
                            pass_info['app_user'] = {
                                "phone": app_user.get("phone", ""),
                                "outer_app_user_id": app_user.get("outer_app_user_id", ""),
                                "app_user_id": app_user.get("app_user_id", None)
                            }
            brake_card_id = brake_pass.get("brake_card", None)
            if brake_card_id:
                brake_card = get_data("brake_card", brake_card_id)
                if brake_card:
                    pass_info['brake_card'] = {
                        "card_no": brake_card.get("card_no", None),
                        "card_owner": brake_card.get("card_owner", {}),
                    }
            db.brake_pass.update({"_id": brake_pass['_id']}, {"$set": {"pass_info": pass_info}})
        print("finish %s brake_pass" % brake_pass_list_count)
        brake_pass_list = db.brake_pass.find({"pass_info": None}).limit(page_size)
        brake_pass_list_count = brake_pass_list.count()


def update_brake_machine():
    brake_machine_list = db.brake_machine.find({"hardware_version": None})
    for brake_machine in brake_machine_list:
        mac = brake_machine.get("mac", "")
        version_id = brake_machine.get("version", "")
        if version_id:
            version = get_data("brake_version", version_id)
            if version:
                firmware_version = version.get("version", "")
                db.brake_machine.update({"_id": brake_machine['_id']}, {"$set": {"firmware_version": firmware_version}})
        if len(mac) == 12:
            hardware_version = ""
            if mac[-6:] >= '001100' and mac[-6:] <= '003a04':
                hardware_version = "QC201_V1.1"
            elif mac[-6:] >= '003a05' and mac[-6:] <= '003ad7':
                hardware_version = "QC201_V2.0"
            elif mac[-6:] >= '003ad8' and mac[-6:] <= '004adc':
                hardware_version = "QC201_V1.1"
            elif mac[-6:] >= '004add' and mac[-6:] <= '005c56':
                hardware_version = "QC201_V2.0"
            elif mac[-6:] >= '005c57' and mac[-6:] <= '00648b':
                hardware_version = "QC201_V1.1"
            elif mac[-6:] >= '00648c' and mac[-6:] <= '007cc5':
                hardware_version = "QC201_V2.0"
            db.brake_machine.update({"_id": brake_machine['_id']}, {"$set": {"hardware_version": hardware_version}})


db.brake_machine.update_many({}, {"$unset": {"current_version": True}})
db.brake_machine.update_many({}, {"$unset": {"position_by_learn": True}})
db.brake_machine.update_many({}, {"$unset": {"open_door_app_user_list": True}})
update_brake_machine()
print("brake_machine finished")

db.sentry_visitor.update_many({}, {"$unset": {"apartment": True}})
update_sentry_visitor(1000)
print("sentry_visitor finished")

db.brake_pass.update_many({}, {"$unset": {"position": True}})
db.brake_pass.update_many({}, {"$unset": {"position_str": True}})
db.brake_pass.update_many({}, {"$unset": {"app_user": True}})
db.brake_pass.update_many({}, {"$unset": {"apartment": True}})
update_brake_pass(1000)
print("brake_pass finished")

