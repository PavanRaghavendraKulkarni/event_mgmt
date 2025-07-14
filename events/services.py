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