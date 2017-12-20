# --*-- coding:utf-8 --*--
import logging

logger = logging.getLogger('qding')


def jsonResponse():
    def decorator(view_fun):
        def __jp(*args, **kwgs):
            result = view_fun(*args, **kwgs)
            # if not result['err']:
            # if not result['data']['flag'] == 'N':
            #     return result
            moudle_name = view_fun.__module__
            class_name = args[0].__class__.__name__
            method_name = view_fun.__name__
            logger.debug("---------------------------")
            logger.debug("---------------------------")
            logger.debug("######## [%s]-[%s]-[%s] ########" % (moudle_name, class_name, method_name))
            logger.debug('>>> params:')
            logger.debug(kwgs)
            logger.debug(args[1:])
            logger.debug('>>> result:')
            logger.debug(result)
            return result

        return __jp

    return decorator
