import random
import string


def generate_code(length):
    return ''.join(random.choices(
        string.ascii_uppercase.replace('O', '').replace('I', '') +
        string.digits.replace('0', '').replace('1', ''), k=length))
