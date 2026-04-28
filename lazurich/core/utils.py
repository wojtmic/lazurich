import random
import string

_ALPHABET = string.ascii_lowercase + string.digits

def gen_id() -> str:
    return ''.join(random.choices(_ALPHABET, k=8))
