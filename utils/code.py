from os import urandom
from binascii import hexlify


def generate_code(length: int = 20):
    return hexlify(urandom(length)).decode()
