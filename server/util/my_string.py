__all__ = ['average_split', 'is_contains_chinese', 'is_chinese', 'is_num']

import re


def average_split(msg, count):
    l = len(msg)
    if l < count:
        return tuple(msg, )
    else:
        result = list()
        fragmentLen = int(l / count)
        if fragmentLen != l / count:
            fragmentLen += 1
        for i in range(count):
            result.append(msg[i * fragmentLen:(i + 1) * fragmentLen])
        return tuple(result)


# 判断一个unicode是否是汉字
def is_chinese(uchar):
    if '\u4e00' <= uchar <= '\u9fff':
        return True
    else:
        return False


def is_contains_chinese(my_str):
    for c in my_str:
        if is_chinese(c):
            return True
    return False


def is_num(str_num):
    return re.match(r'^\d+(.\d+)?$', str_num) is not None


if __name__ == '__main__':
    average_split('1234567890', 3)
