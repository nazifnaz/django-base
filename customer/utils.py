import calendar
import datetime
from time import time


def get_current_year():
    return datetime.datetime.now().year


def unique_id(prefix=''):
    return prefix + str(get_current_year()) + hex(int(time()))[2:10] + hex(int(time() * 1000000) % 0x100000)[2:7]


def get_month_name(number):
    return calendar.month_name[number].lower()
