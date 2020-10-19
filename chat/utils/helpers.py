from string import digits, ascii_letters

from Crypto.Random import random


def generate_random(length: int = 32):
    # pip3 uninstall crypto
    # pip3 uninstall pycrypto
    # pip3 install pycryptodome
    return "".join(random.choice(digits + ascii_letters) for _ in range(length))
