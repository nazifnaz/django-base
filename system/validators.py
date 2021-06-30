import datetime

import pytz
from dateutil import parser
from django.core.exceptions import ValidationError


def validate_past_date(value):
    if not value:
        return
    if isinstance(value, str):
        date = parser.parse(value).date()
    else:
        date = value
    if date > datetime.datetime.today().date():
        raise ValidationError('Date should be a past value')


def validate_future_date(value):
    if not value:
        return
    if isinstance(value, str):
        date = parser.parse(value).date()
    else:
        date = value
    if date < datetime.datetime.today().date():
        raise ValidationError('Date should be a future value')
