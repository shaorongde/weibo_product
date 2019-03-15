#! python3
"""
简单的获取列表
新增对象
获取对象详细信息
更新对象
删除对象
"""
__all__ = ['generate_dict_list', 'generate_dict_from_dict', 'generate_dict_from_object',
           'generate_contains_search_dict',
           'generate_equal_search_dict', 'generate_date_filter']

from datetime import timedelta


def generate_dict_list(query_set, attr_list):
    """
    获取列表
    :param query_set:
    :param attr_list:
    :return:
    """
    count = len(query_set)
    if count == 0:
        return []
    response = [generate_dict_from_object(c, attr_list) for c in query_set]
    return response


def generate_dict_from_object(obj, attr_list):
    """
    根据 attr_list 从对象obj中获取属性，然后生成dict
    :param obj:
    :param attr_list:
    是一个tuple，每一项是tuple或str，
    tuple第一项是属性名，第二项为别名
    str的话直接就是属性名
    如果是关系数据，直接在属性中使用点号，最后生成的属性名是将点号替换为下划线
    :return:
    """
    result = {}

    for item in attr_list:
        if type(item) is tuple:
            # 如果有别名
            attr, alias = item
            if alias is None:
                raise Exception('别名不能为空')
            result[alias] = get_value(obj, attr)
        elif type(item) is str:
            # 没有别名
            result[item.replace('.', '_').replace('()', '')] = get_value(obj, item)
        else:
            raise Exception('attr_list中的项只能是字符串或者是tuple')
    return result


def generate_dict_from_dict(source, attr_list, force=True):
    result = {}
    for item in attr_list:
        if type(item) is tuple:
            # 如果有别名
            attr, alias = item
            if alias is None:
                raise Exception('别名不能为空')
            try:
                result[alias] = source[attr]
            except KeyError:
                if force:
                    raise Exception('没有属性' + attr)
        elif type(item) is str:
            # 没有别名
            try:
                result[item] = source[item]
            except KeyError:
                if force:
                    raise Exception('没有属性' + item)
        else:
            raise Exception('attr_list中的项只能是字符串或者是tuple')
    return result


def get_value(obj, attr_or_method):
    my_eval = 'obj.' + attr_or_method
    return eval(my_eval)


def generate_contains_search_dict(param_list, **kwargs):
    """
    生成 字符匹配包含 的搜索dict
    :param param_list:
    :param search_param:
    :param kwargs:
    :return:
    """
    search_param = {}
    for p in param_list:
        if p in kwargs:
            search_param[p + '__contains'] = kwargs[p]
    return search_param


def generate_equal_search_dict(param_list, **kwargs):
    """
    生成 值判等 的搜索dict
    :param param_list:
    :param search_param:
    :param kwargs:
    :return:
    """
    search_param = {}
    for p in param_list:
        if p in kwargs:
            search_param[p] = kwargs[p]
    return search_param


def generate_date_filter(date_param_name, date_start=None, date_end=None):
    """
    生成时间筛选
    """
    search_param = dict()
    if date_start is not None:
        search_param[date_param_name + '__gte'] = date_start
    if date_end is not None:
        search_param[date_param_name + '__lt'] = date_end + timedelta(days=1)
    return search_param
