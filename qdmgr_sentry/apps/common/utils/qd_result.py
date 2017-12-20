# --*-- coding:utf-8 --*--
def get_default_result():
    return {'err': 0, 'msg': 'success', 'log': '', 'test_code': 0, 'data': {'flag': 'Y'}}


def set_err_msg(result, msg, err=0, log=None, test_code=0, flag='N'):
    result['test_code'] = test_code
    result['err'] = err
    result['msg'] = msg
    result['log'] = log
    result['data']['flag'] = flag
    return result

