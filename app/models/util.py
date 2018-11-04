import random
import string


def normalize_email(email) -> str:
    """
    Normalize the email address by making the domain part of it lowercase.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = email_name + '@' + domain_part.lower()
    return email


def generate_code(length) -> str:
    return ''.join(random.choices(
        string.ascii_uppercase.replace('O', '').replace('I', '') +
        string.digits.replace('0', '').replace('1', ''), k=length))
