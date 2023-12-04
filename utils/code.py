from binascii import hexlify
from os import urandom


def generate_code(length: int = 20):
    return hexlify(urandom(length)).decode()
