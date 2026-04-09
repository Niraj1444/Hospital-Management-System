from datetime import datetime


def is_empty(value):
    return not str(value).strip()


def is_valid_phone(phone):
    phone = phone.strip()
    return phone.isdigit() and len(phone) in (10, 11, 12)


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False
