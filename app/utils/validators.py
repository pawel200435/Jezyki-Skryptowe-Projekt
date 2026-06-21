import re
from datetime import datetime

def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$' # test@test.com
    return re.match(email_pattern, email) is not None

def is_date_in_future(date_obj):
    """
    Check if data is from future
    """
    if date_obj and date_obj.date() > datetime.now().date():
        return True
    
    return False

def is_range_invalid(date_from, date_to):
    """
    Check if date range is invalid (data_from > data_to)
    """
    if date_from and date_to:
        if date_from > date_to:
            return True
    
    return False

def validate_and_parse_dates(date_from_str, date_to_str):
    """
    Date validator, returns tuple: (date_from, date_to, error_msg)
    """
    date_from = None
    date_to = None

    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
            if is_date_in_future(date_from):
                return None, None, "Date 'from' can't be from future"
        
        if date_to_str:
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d")
            if is_date_in_future(date_to):
                return None, None, "Date 'to' can't be from future"
            date_to = datetime.strptime(f"{date_to_str} 23:59:59", '%Y-%m-%d %H:%M:%S')

        if is_range_invalid(date_from, date_to):
            return None, None, "Invalid dates: 'from' > 'to' must be 'from' < 'to'"
        
    except ValueError:
        return None, None, "Invalid date format. Need YYYY-MM-DD."

    return date_from, date_to, None