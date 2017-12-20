# -*- coding: utf-8 -*-

from django.db import connection as db_conn
import datetime, traceback

import logging

logger = logging.getLogger('qding')


def query_many(sql_tpl, sql_params=[], log=False):
    cursor = db_conn.cursor()
    row_cnt = 0

    sql_tpl = sql_tpl.strip()
    try:
        row_cnt = cursor.execute(sql_tpl, sql_params)
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.debug(sql_tpl)
        logger.debug(sql_params)
        raise e

    rows = dictfetchall(cursor)
    cursor.close()

    return rows


def query_one(sql_tpl, sql_params=[], log=False):
    rows = query_many(sql_tpl, sql_params, log)

    if len(rows) > 0:
        return rows[0]

    return None


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return_rows = [
        dict(zip(
            [col[0] for col in desc],
            [attr.strftime('%Y-%m-%d %H:%M:%S') if isinstance(attr, datetime.datetime) else attr for attr in row]
        )) for row in cursor.fetchall()
        ]

    return return_rows


def execute_one(sql_tpl, sql_params=[], log=False):
    cursor = db_conn.cursor()
    row_cnt = 0

    sql_tpl = sql_tpl.strip()
    insert_flag = False if sql_tpl[:6].lower() != 'insert' else True
    insert_id = 0

    try:
        row_cnt = cursor.execute(sql_tpl, sql_params)

        if insert_flag:
            insert_id = cursor.db.connection.insert_id()

        cursor.db.connection.commit()

    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.debug(sql_tpl)
        logger.debug(sql_params)
        raise e

    cursor.close()

    if not row_cnt and log:
        logger.debug('row_cnt is zero...')
        logger.debug(sql_tpl)
        logger.debug(sql_params)

    if insert_flag:
        return insert_id

    return row_cnt


def execute_batch(sql_tpl, sql_params=[], log=False):
    cursor = db_conn.cursor()
    row_cnt = 0

    sql_tpl = sql_tpl.strip()
    try:
        row_cnt = cursor.executemany(sql_tpl, sql_params)
        cursor.db.connection.commit()
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.debug(sql_tpl)
        logger.debug(sql_params)
        raise e

    cursor.close()

    if not row_cnt and log:
        logger.debug('row_cnt is zero...')
        logger.debug(sql_tpl)
        logger.debug(sql_params)

    return row_cnt
