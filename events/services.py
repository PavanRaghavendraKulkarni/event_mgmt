import pytz
from django.utils import timezone
from datetime import datetime

IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.UTC

def to_ist(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = UTC.localize(dt)
    return dt.astimezone(IST)

def to_utc(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        dt = IST.localize(dt)
    return dt.astimezone(UTC)

def to_local(dt, tz_str):
    import pytz
    if dt is None:
        return None
    tz = pytz.timezone(tz_str)
    if timezone.is_naive(dt):
        dt = UTC.localize(dt)
    return dt.astimezone(tz)

def to_utc_from_local(dt, tz_str):
    import pytz
    if dt is None:
        return None
    tz = pytz.timezone(tz_str)
    if timezone.is_naive(dt):
        dt = tz.localize(dt)
    return dt.astimezone(UTC) 