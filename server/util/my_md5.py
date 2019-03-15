__all__ = ['generate_md5']

import hashlib


def generate_md5(msg):
    md5 = hashlib.md5(msg.encode('utf-8')).hexdigest()
    return md5
