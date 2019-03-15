__all__ = ['generate_token', 'analyze_token', 'verify_token']

import re
import time

from . import my_md5, my_string

'''
token由两部分组成，一部分是账号字符串的md5，另一部分是失效的时间戳
两个字符串分成5段，再次拼接在一起
'''


def generate_token(username):
    flag = my_string.average_split(my_md5.generate_md5(username), 5)
    mytime = my_string.average_split(str(int(time.time()) + 86400 * 7), 5)
    return flag[0] + mytime[0] + flag[1] + mytime[1] + flag[2] + mytime[2] + flag[3] + mytime[3] + flag[4] + mytime[4]


def analyze_token(token):
    result = my_string.average_split(token, 5)
    flag = ''
    mytime = ''
    for x in result:
        flag += x[:-2]
        mytime += x[-2:]
    return tuple([flag, int(mytime)])


def verify_token(token):
    """
    校验token，空，42位长度，是否包含非字母字符
    """
    if not token:
        return False
    elif len(token) != 42:
        return False
    else:
        return re.match(r'^\w+$', token) is not None


if __name__ == '__main__':
    print(analyze_token(generate_token('hui')))
