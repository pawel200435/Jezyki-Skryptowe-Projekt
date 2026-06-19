import re

def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$' # test@test.com
    return re.match(email_pattern, email) is not None
