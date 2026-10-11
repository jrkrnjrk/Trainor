from datetime import datetime

def to_datetime(snowflake):
    return datetime.utcfromtimestamp(((int(snowflake) >> 22) + 1420070400000) / 1000.0)

def from_datetime(dt):
    return int((dt.timestamp() * 1000 - 1420070400000) << 22)

def to_unix(snowflake):
    return ((int(snowflake) >> 22) + 1420070400000) / 1000.0
