__all__ = ['verify_token', 'validate_args', 'fetch_object']

from functools import wraps

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import QueryDict
from django.shortcuts import redirect

from . import response


def verify_token(model_class=None):
    """
    被装饰的方法进行用户身份验证，并且当前用户模型存为request.user，
    用户令牌作为请求头X-User-Token进行传递，浏览器访问则获取session
     """

    def wrapper(func):

        @wraps(func)
        def inner(self, request, *args, **kwargs):

            token = request.COOKIES.get('TOKEN')
            # 处理api请求
            if model_class:
                if token:
                    users = model_class.objects.filter(token=token)
                    if len(users) != 1:
                        return response.err_response_token()
                    user = users[0]
                    # 验证通过
                    kwargs['me'] = user
                    return func(self, request, *args, **kwargs)
                else:
                    return response.err_response_token()
            else:
                if token:
                    return func(self, request, *args, **kwargs)
                else:
                    return redirect('/login/')

        return inner

    return wrapper


def validate_args(myargs):
    """
    对被装饰的方法利用 "参数名/表单模型" 字典进行输入数据验证，验证后的数据
    作为关键字参数传入view函数中，若部分数据非法则直接返回400 Bad Request
    HowieWang修改：
    能够处理request.FILES中的参数
    能够处理url中的参数，即参数本身就在kwargs
    """

    def decorator(func):

        @wraps(func)
        def inner(self, request, *args, **kwargs):
            if request.method == 'GET':
                data = request.GET
            elif request.method == 'POST':
                data = request.POST
            else:
                data = QueryDict(request.body)
            for k, v in myargs.items():
                try:
                    if k in kwargs:
                        request_value = kwargs.get(k)
                    else:
                        request_value = data.get(k)
                        if request_value is None:
                            request_value = request.FILES[k]
                    kwargs[k] = v.clean(request_value)
                except KeyError:
                    if v.required:
                        # 缺少参数
                        return response.err_response_miss_param(k)
                except ValidationError as e:
                    # 参数不符合要求
                    return response.err_response_value_err(k, request_value, ','.join(e))
            return func(self, request, *args, **kwargs)

        return inner

    return decorator


def fetch_object(model_class, object_name, arg_name=None):
    """
    根据参数 "xxx_id" 在执行view函数前提前取出某个模型实例，
    若关键字参数中没有 "xxx_id" 则忽略
    HowieWang修改：
    如果kwargs中XXX不是object_name,则可以传入arg_name
    """

    def decorator(func):

        @wraps(func)
        def inner(*args, **kwargs):
            arg = arg_name or (object_name + '_id')

            if arg in kwargs:
                obj_id = kwargs.pop(arg)
                try:
                    obj = model_class.objects.get(pk=obj_id)
                except ObjectDoesNotExist:
                    return response.err_response_pk(arg, obj_id)
                else:
                    # 如果没有异常，执行这里
                    kwargs[object_name] = obj
            return func(*args, **kwargs)

        return inner

    return decorator
