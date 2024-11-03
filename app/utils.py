import datetime


def get_current_time():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
