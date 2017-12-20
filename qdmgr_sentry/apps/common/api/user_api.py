# -*- coding: utf-8 -*-
import json
import hashlib
import traceback
import datetime
import time

from apps.basedata.classes.Basedata_Project import Basedata_Project
from settings.const import CONST
from apps.common.utils import qd_result, validate
from apps.web.classes.Web_User import Web_User
from apps.common.utils.view_tools import jsonResponse
from apps.web.classes.App_Download import App_Download
from apps.common.utils.request_api import request_bj_server
from apps.common.utils.xutil import create_random_num
from apps.common.utils.redis_client import rc


class Web_User_Api():
    """
    @note: 对web用户的操作封装在此类
    """

    @jsonResponse()
    def add_web_user(self, role=None, access=None, username=None, phone=None, password=None, area=[]):
        """
        @note: access url： /user_api/Web_User_Api/add_web_user/1/
        @param role: role, 2-property admin, 3-configure admin, 4-data scan
        @param access: access, 1-common， 2-city， 3-property， 4-super
        @param username: user name, 1-10 characters, include chinese
        @param phone: phone, 11 digits
        @param password: password, 4-100 characters
        @param area: area list, eg:['1789']
        @return: {'err': 0, 'msg': 'success', 'log': '', 'test_code': 0, 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()

            role_flag, role_str = validate.validate_list_member_attr('user role', str(role), ['2', '3', '4'])
            if not role_flag: return qd_result.set_err_msg(result, role_str)

            access_flag, access_str = validate.validate_list_member_attr('user access', str(access), ['1', '2', '3', '4'])
            if not access_flag: return qd_result.set_err_msg(result, access_str)
            access = int(access)

            area = json.loads(area) if isinstance(area, str) else area
            validate_area_flag, validate_area_str = validate.validate_area(area, access)
            if not validate_area_flag: return qd_result.set_err_msg(result, validate_area_str)

            area_flag, area, area_str, area_ret = Web_User.check_area(area, access)
            if not area_flag: return qd_result.set_err_msg(result, area_ret)

            if int(role) == 2:
                if not username: return qd_result.set_err_msg(result, 'please input username')
                if not phone: return qd_result.set_err_msg(result, 'please input phone')

                pass_num = create_random_num(6)
                password = hashlib.md5(pass_num.encode(encoding='utf_8')).hexdigest()
            elif int(role) == 3:
                if not phone: return qd_result.set_err_msg(result, 'please input phone')
                username = None
            else:
                if not username: return qd_result.set_err_msg(result, 'please input username')
                phone = None

            password_flag, password_str = validate.validate_str("password", password, 4, 100)
            if not password_flag: return qd_result.set_err_msg(result, password_str)
            password = str(password)

            if username:
                username_flag, user_name_str = validate.validate_contain_chinese_str("username", str(username), 1, 10)
                if not username_flag: return qd_result.set_err_msg(result, user_name_str)

                username = str(username)
                if Web_User.objects(username=username): return qd_result.set_err_msg(result, "%s exists" % username, test_code=2)

            if phone:
                phone_flag, phone_str = validate.validate_phone(str(phone))
                if not phone_flag: return qd_result.set_err_msg(result, phone_str)

                phone = str(phone)
                if Web_User.objects(phone=phone): return qd_result.set_err_msg(result, "%s exists" % phone, test_code=1)

            if int(role) == 2:
                try:
                    url = 'smsRequest?body={"mobile":"%s","content":"尊敬的用户，请凭账号：%s，密码：%s，登陆%s，' \
                          '查询%s的通行数据。"}' % (phone, username, pass_num, CONST['base']['host'], area_str)
                    request_bj_server(method_url=url, method_params={}, post_flag=False)
                except Exception as e:
                    qd_result.set_err_msg(result, e, 1, traceback.format_exc())

                role = [2, 3]
            else:
                role = [int(role)]

            user_obj = Web_User(role_list=role, access=access, username=username, password=password, phone=phone, area=area, area_str=area_str)
            user_obj.save()

        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def web_login(self, username=None, password=None):
        """
        @note: access url： /user_api/Web_User_Api/web_login/
        @param username: user name,1-10 characters, include chinese
        @param password: password, 4-100 characters
        @return: {'err': 0, 'msg': 'success', 'log': '', 'data': {'flag': 'Y', 'url': '/content#/device_monitoring', 'web_user': {'user_type': '1', 'status': '1', 'id': '579109cacdc8722007297fa2', 'project_list': [{'project': '千丁互联', 'province': '西藏', 'city': '中陲'}], 'phone': '18188621491', 'username': 'test'}}, 'test_code': 0}
        """
        try:
            result = qd_result.get_default_result()
            result['data']['url'] = '/'

            raw_query = {"$or": [{"username": str(username)}, {"phone": str(username)}], "password": str(password)}
            web_user = Web_User.objects(__raw__=raw_query).first()
            if not web_user: return qd_result.set_err_msg(result, '用户名或密码错误')

            if web_user.status != "1":
                return qd_result.set_err_msg(result, '用户没有激活')
            if [3] == web_user.role_list:
                return qd_result.set_err_msg(result, '对不起，您不能登录该系统，请联系管理员')
            else:
                web_user_dict = web_user.get_web_user_info()
                web_user_dict['project_list'] = Web_User.get_access_project_info(user_obj=web_user)
                if not web_user_dict['project_list']: return qd_result.set_err_msg(result, '您未绑定任何社区，请联系管理员')
                web_user_dict['project_list'].sort(key=lambda x: x['city'])
                if 1 in web_user.role_list:
                    result['data']['url'] = '/manage/content/#/scan_data'
                else:
                    result['data']['url'] = '/content#/device_monitoring'
                result['data']['web_user'] = web_user_dict
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_web_user_by_filter(self, role=None, access=None, username=None, phone=None, page_no=1, page_size=0):
        """
        @note: access url： /user_api/Web_User_Api/get_web_user_by_filter/1/
        @param role:user role 2-property admin, 3-configure admin, 4-data scan
        @param access: user access
        @param username:username
        @param phone: phone
        @param page_no: page no
        @param page_size: page size
        @return: {'log': '', 'data': {'pagination': {'total_count': 1, 'page_no': 1, 'page_size': 0}, 'web_user_list': [{'project_list': [{'project': '千丁互联', 'province': '西藏', 'city': '中陲'}], 'phone': '18188621491', 'status': '1', 'username': 'test', 'user_type': '1', 'id': '579109cacdc8722007297fa2'}], 'flag': 'Y'}, 'err': 0, 'msg': 'success', 'test_code': 0}
        """
        try:
            result = qd_result.get_default_result()

            page_flag, page_str = validate.validate_pagination(page_size, page_no)
            if not page_flag: return qd_result.set_err_msg(result, page_str)

            raw_query = {"role_list": {"$ne": 1}}
            d = {"username": username, "phone": phone}

            for k, v in d.items():
                if v: raw_query.update({k: {"$regex": v}})

            role_flag, role_str = validate.validate_num(str(role), 'role')
            access_flag, access_str = validate.validate_num(str(access), 'access')

            if role_flag: raw_query.update({"role_list": int(role)})
            if access_flag: raw_query.update({"access": int(access)})

            db_web_user_list = Web_User.objects(__raw__=raw_query)
            if page_size: db_web_user_list = db_web_user_list.skip((int(page_no) - 1) * int(page_size)).limit(int(page_size))

            web_user_list = [web_user.get_web_user_info() for web_user in db_web_user_list]
            result['data']['web_user_list'] = web_user_list
            result['data']['pagination'] = {
                'page_no': page_no,
                'page_size': page_size,
                'total_count': db_web_user_list.count(),
            }
        except Exception as e:
            qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def get_area(self, user_id=None):
        """
        @note: access url： /user_api/Web_User_Api/get_area/1/
        @param user_id: user id
        @return: {'err': 0, 'msg': 'success', 'log': '', 'test_code': 0, 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()

            web_user = Web_User.objects(id=str(user_id)).first()
            if not web_user: return qd_result.set_err_msg(result, "%s not exists" % user_id)

            d = {
                "1": ("outer_project_id", "project"),
                "2": ("outer_city_id", "city"),
                "3": ("outer_property_id", "property_name")
            }

            area_dict_map = {}

            attr_id, attr_name = d[str(web_user.access)]

            bp_list = Basedata_Project.objects(__raw__={attr_id: {"$in": web_user.area}})

            for bp in bp_list:
                area_id, area_str = getattr(bp, attr_id, ""), getattr(bp, attr_name, "")
                if not area_id or area_id not in web_user.area: continue

                area_dict_map[area_id] = {"area_id": area_id, "area_str": area_str}

            result['data']['area_dict_list'] = list(area_dict_map.values())
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def bind_area(self, user_id=None, area=[]):
        """
        @note: access url： /user_api/Web_User_Api/bind_area/1/
        @param user_id: user id
        @param area: area, eg:[{"1789"}]
        @return: {'err': 0, 'msg': 'success', 'log': '', 'test_code': 0, 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()

            web_user = Web_User.objects(id=str(user_id)).first()
            if not web_user: return qd_result.set_err_msg(result, "%s not exists" % user_id)

            area = json.loads(area) if isinstance(area, str) else area
            validate_area_flag, validate_area_str = validate.validate_area(area, web_user.access)
            if not validate_area_flag: return qd_result.set_err_msg(result, validate_area_str)

            area_flag, area, area_str, area_ret = Web_User.check_area(area, web_user.access)
            if not area_flag: return qd_result.set_err_msg(result, area_ret)

            web_user.area = area
            web_user.area_str = area_str
            web_user.save()

        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def modify_user(self, user_id=None, username=None, old_password=None, password=None, status=None, phone=None):
        """
        @note: access url： /user_api/Web_User_Api/modify_user/1/
        @param user_id: user id
        @param username: user name
        @param old_password: old password
        @param password: user password
        @param status: user status
        @param phone: user phone
        @return: {'err': 0, 'msg': 'success', 'log': '', 'test_code': 0, 'data': {'flag': 'Y'}}
        """
        try:
            result = qd_result.get_default_result()

            web_user = Web_User.objects(id=str(user_id)).first()
            if not web_user: return qd_result.set_err_msg(result, "用户数据不存在")

            def _change_password(_password):
                web_user.password = _password
                web_user.updated_time = datetime.datetime.now()
                web_user.password_num = 0
                web_user.created_time = datetime.datetime.now()

            if username:
                username_flag, username_str = validate.validate_contain_chinese_str("username", str(username), 1, 10)
                if not username_flag: return qd_result.set_err_msg(result, username_str)
                if Web_User.objects(username=str(username)): return qd_result.set_err_msg(result, "用户名已经存在")
                web_user.username = str(username)
            elif password and not old_password:
                password_flag, password_str = validate.validate_str("password", str(password), 4, 100)
                if not password_flag: return qd_result.set_err_msg(result, password_str)
                _change_password(str(password))
            elif password and old_password:
                if web_user.password != str(old_password).strip(): return qd_result.set_err_msg(result, '旧密码错误')
                password_flag, password_str = validate.validate_str("password", str(password), 4, 100)
                if not password_flag: return qd_result.set_err_msg(result, password_str)
                _change_password(str(password))
            elif status:
                status_flag, status_str = validate.validate_status(str(status))
                if not status_flag: return qd_result.set_err_msg(result, status_str)
                web_user.status = str(status)
            elif phone:
                phone_flag, phone_str = validate.validate_phone(str(phone))
                if not phone_flag: return qd_result.set_err_msg(result, phone_str)
                if Web_User.objects(phone=str(phone)): return qd_result.set_err_msg(result, "该手机号已经存在")
                web_user.phone = str(phone)
            web_user.save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def forget_password(self, phone=None, verify_code=None):
        """
        @note: 用途：忘记密码
        @note: 访问url： /user_api/Web_User_Api/forget_password/
        @note: 测试demo:{phone:"18188621491",verify_code:"655965"}
        @param phone: 用户手机号
        @param verify_code: 验证码
        @return: result{"data":{"flag":"Y"}},Y表示成功，N表示失败
        """
        try:
            result = qd_result.get_default_result()

            web_user = Web_User.objects(phone=str(phone)).first()
            if not web_user: return qd_result.set_err_msg(result, '手机号不存在')

            verify_dic = rc.get(phone)
            if not verify_dic: return qd_result.set_err_msg(result, '验证码超时')

            verify_dic = json.loads(verify_dic.decode('utf8'))
            server_verify_code = verify_dic.get("verify_code", "")
            if str(server_verify_code) != str(verify_code): return qd_result.set_err_msg(result, '验证码错误')

            new_password = create_random_num(8)
            new_password_md5 = hashlib.md5(new_password.encode("utf8")).hexdigest()
            web_user.password = new_password_md5
            web_user.save()
            url = 'smsRequest?body={"mobile":"%s","content":"尊敬的用户，您的新密码是：%s"}' % (phone, new_password)
            request_bj_server(method_url=url, method_params={}, post_flag=False)
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def remove_web_user(self, user_id=None):
        """
        @note: 用途 ： 删除web用户
        @note: 访问url： /user_api/Web_User_Api/remove_web_user/1/
        @param user_id:用户的id
        @return: result{"data":{"flag":"Y"}},Y表示删除成功，N表示删除失败
        """
        try:
            result = qd_result.get_default_result()
            web_user = Web_User.objects(id=str(user_id)).first()

            if not web_user: return qd_result.set_err_msg(result, '%s not exists' % user_id)
            web_user.delete()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result

    @jsonResponse()
    def brake_config_login(self, province=None, city=None, community=None, phone=None, brake_config_password=None):
        """
        @note: access url： /brake_config_login
        @note: test demo:{province:"中陲",city:"中陲",community:"千丁嘉园",phone:"18188621491",brake_config_password:"e1819b2e1ff047ce6d4cc98bc4d7c5aa"}
        @param province: province
        @param city: city
        @param community: community
        @param phone: phone
        @param brake_config_password: brake config password
        @return: {'log': '', 'data': {'flag': 'Y', 'server_time': 1469180678, 'web_user': {'user_type': '1', 'phone': '18188621491', 'province': '西藏', 'city': '中陲', 'community': '千丁互联'}}, 'msg': 'success', 'test_code': 0, 'err': 0}
        """
        try:
            result = qd_result.get_default_result()
            config_password_flag, config_password_str = validate.validate_password(str(brake_config_password))
            if not brake_config_password or not config_password_flag:
                result['msg'] = config_password_str
                result['test_code'] = 2
                result['data']['flag'] = 'N'
                return result
            web_user = Web_User.objects(phone=str(phone), password=str(brake_config_password)).first()
            if not web_user:
                result['msg'] = "phone or password wrong"
                result['test_code'] = 3
                result['data']['flag'] = 'N'
                return result
            if web_user.status != "1":
                result['msg'] = "user not active"
                result['test_code'] = 4
                result['data']['flag'] = 'N'
                return result
            result['data']['web_user'] = {
                "user_type": web_user.user_type,
                "phone": web_user.phone,
            }
            result['data']['web_user']['province'] = province
            result['data']['web_user']['city'] = city
            result['data']['web_user']['community'] = community
            result['data']['server_time'] = int(time.time())
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result


class App_Download_Api():
    """
    @note: 对手机用户下载北京APP的操作封装在此类
    """

    @jsonResponse()
    def download_app(self, agent):
        """
        @note: 用途：记录用户下载APP的数据
        @note: 访问url： /user_api/App_Download_Api/download_app/
        @param agent: 用户agent信息
        @return: result{"data":{"flag":"Y"}},Y表示登录成功，N表示登录失败
        """
        try:
            result = qd_result.get_default_result()
            App_Download(agent=agent).save()
        except Exception as e:
            result = qd_result.set_err_msg(result, e, 1, traceback.format_exc())
        return result
