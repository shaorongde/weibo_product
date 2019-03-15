from django.http import JsonResponse

__all__ = ['correct_response', 'err_response', 'err_response_miss_param', 'err_response_not_belong',
           'err_response_permission', 'err_response_pk', 'err_response_token', 'err_response_user_lock',
           'err_response_value_err']


def response_code_and_data(code, data):
    response = dict(code=code, )
    if data is not None:
        response['data'] = data
    return JsonResponse(response)


def correct_response(data=None):
    """正确时的返回

    :param data: 字典
    """
    return response_code_and_data(0, data)


def err_response(code, data=None):
    return response_code_and_data(code, data)


def err_response_token():
    """
    token过期，错误等，需要重新登录
    """
    return err_response(-1)


def err_response_permission():
    """
    权限不足，无法操作
    """
    return err_response(-2)


def err_response_user_lock():
    """
    账户锁定，请联系管理员解锁账户
    """
    return err_response(-3)


def err_response_miss_param(param_name):
    """
    缺少参数
    """
    return err_response(-4, dict(param_name=param_name))


def err_response_value_err(param_name, param_value, format_require):
    """
    参数值不符合参数要求
    """
    return err_response(
        -5, dict(
            param_name=param_name,
            param_value=param_value,
            require=format_require,
        )
    )


def err_response_pk(param_name, param_value):
    """
    主键错误，新增表示主键已存在，删改查表示主键不存在
    """
    return err_response(-6, dict(
        param_name=param_name,
        param_value=param_value,
    ))


def err_response_not_belong(
        parent_param_name, parent_param_value, children_param_name, children_param_value
):
    """
    例如，公司A有员工，a,b,c，公司B有员工，d,e,f
    公司A无权开除员工d，因为d不属于公司A
    parent_param_name 公司的参数名
    parent_param_value 公司的参数值
    children_param_name 员工的参数名
    children_param_value 员工的参数值
    """
    return err_response(-7, dict(
        parent_param_name=parent_param_name,
        parent_param_value=parent_param_value,
        children_param_name=children_param_name,
        children_param_value=children_param_value,
    ))
