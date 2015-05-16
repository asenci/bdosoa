"""
bdosoa - helper functions
"""

import string

from random import SystemRandom


def gen_token(size=32):
    """Generate random tokens

    :param int size: Size of the generated token
    :return: A random token
    :rtype: str
    """

    charlist = string.digits + string.letters

    token = [SystemRandom().choice(charlist) for _ in range(size)]

    return ''.join(token)
