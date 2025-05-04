import random
import string

def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    chars = ''
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += '!@#$%^&*()-_=+[]{}|;:,.<>?/'
    if not chars:
        raise ValueError('At least one character set must be selected')
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))
