import time
from datetime import datetime


def get_day_timestamp(index=0, str_format='%Y-%m-%d'):
    str_day = time.strftime(str_format, time.localtime(time.time() + index * 24 * 60 * 60))
    return int(time.mktime(time.strptime(str_day, str_format)))


def get_day_datetime(index=0):
    str_day = time.strftime('%Y-%m-%d', time.localtime(time.time() + index * 24 * 60 * 60))
    return datetime.strptime(str_day, "%Y-%m-%d")


def get_time_timestamp(index=0, str_format="%Y-%m-%d %H:%M:%S"):
    str_time = time.strftime(str_format, time.localtime(time.time() + index * 24 * 60 * 60))
    return int(time.mktime(time.strptime(str_time, str_format)))


def get_str_day(index=0, str_format="%Y-%m-%d"):
    str_day = time.strftime(str_format, time.localtime(time.time() + index * 24 * 60 * 60))
    return str_day


def get_str_day_list(day_length=1, str_format="%Y-%m-%d"):
    day_list = []
    for i in range(day_length):
        day_list.append(get_str_day(-i, str_format))
    return day_list


def get_str_day_by_timestamp(timestamp, str_format='%Y-%m-%d', index=0):
    str_day = time.strftime(str_format, time.localtime(int(timestamp) + index * 24 * 60 * 60))
    return str_day


def get_str_day_by_datetime(dt, str_format='%Y-%m-%d'):
    return dt.strftime(str_format)


def get_str_time_by_timestamp(timestamp, str_format="%Y-%m-%d %H:%M:%S"):
    str_time = time.strftime(str_format, time.localtime(timestamp))
    return str_time


def get_timestamp_by_str_day(str_day, str_format='%Y-%m-%d', index=0):
    return int(time.mktime(time.strptime(str_day, str_format))) + index * 24 * 60 * 60


def get_datatime(index=0, str_format="%Y-%m-%d"):
    str_day = get_str_day(index, str_format="%Y-%m-%d")
    return datetime.strptime(str_day, str_format)


def get_datetime_by_str_day(str_day, str_format='%Y-%m-%d', index=0):
    ts = get_timestamp_by_str_day(str_day, str_format, index)
    str_day = time.strftime(str_format, time.localtime(ts))
    return datetime.strptime(str_day, str_format)


def get_datetime_by_timestamp(timestamp, str_format='%Y-%m-%d', index=0):
    str_day = time.strftime(str_format, time.localtime(int(timestamp) + index * 24 * 60 * 60))
    return datetime.strptime(str_day, str_format)


def get_distance_between_days(start_day, end_day, str_format='%Y%m%d'):
    start_day = int(start_day.strftime(str_format))
    end_day = int(end_day.strftime(str_format))
    return end_day - start_day
