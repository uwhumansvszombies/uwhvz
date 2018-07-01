import random
import string


def generate_code(length):
    return ''.join(random.choices(
        string.ascii_uppercase.replace('O', '') + string.digits.replace('0', ''), k=length))
