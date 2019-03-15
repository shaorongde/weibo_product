from django import forms
from django.http import HttpResponse
from django.views import View

# Create your views here.
from api.models import Admin, Clazz, Admin, User, Teacher, Student
from api.service.account import modify_psd
from util import response
from util.decorator import validate_args, fetch_object, verify_token
from util.my_md5 import generate_md5
from util.normal import generate_dict_from_object, generate_dict_list


class InitView(View):
    def get(self, request):
        # init database
        try:
            Admin.objects.get(pk='admin')
        except Admin.DoesNotExist:
            Admin.objects.create(pk='admin', psd=generate_md5('123456'), name='超级管理员')
        return HttpResponse('init finish')


class MyAccountView(View):

    @validate_args({
        'num': forms.CharField(max_length=15),
        'psd': forms.CharField(max_length=32, min_length=32),
    })
    def get(self, request, num, psd, **kwargs):
        """
        登录
        :param request:
        :return:
        错误code
        1：账号或密码错误
        """
        try:
            user = Admin.objects.get(pk=num, psd=psd)
            token = user.update_token()
            res = response.correct_response()
            res.set_cookie('TOKEN', token)
            res.set_cookie('role', User.ROLE_ADMIN)
            return res
        except Admin.DoesNotExist:
            return response.err_response(1)

    @validate_args({
        'num': forms.CharField(max_length=15, min_length=1),
        'name': forms.CharField(max_length=20),
    })
    def post(self, request, num, name, **kwargs):
        """
        注册
        :param request:
        :return:
        """
        try:
            Admin.objects.get(pk=num)
            return response.err_response(1)
        except Admin.DoesNotExist:
            Admin.objects.create(num=num, psd=generate_md5('123'), name=name)
            return response.correct_response()


class InfoView(View):

    @verify_token(Admin)
    def get(self, request, me):
        attr_list = [
            'num',
            'name',
        ]
        res = generate_dict_from_object(me, attr_list)
        return response.correct_response(res)

    @verify_token(Admin)
    def post(self, request, me):
        return response.correct_response()


class PsdView(View):

    @verify_token(Admin)#用户身份验证
    @validate_args({#进行输入数据验证
        'old': forms.CharField(max_length=32, min_length=32),
        'new': forms.CharField(max_length=32, min_length=32),
    })
    def post(self, request, me, old, new):
        """
        修改密码
        :param request:
        :param me:
        :param old:
        :param new:
        :return:
        错误code
        1，原密码错误
        """
        result = modify_psd(Admin, me, old, new)
        if result:
            return response.correct_response()
        else:
            return response.err_response(1)


class ResetPsdView(View):

    @verify_token(Admin)
    @validate_args({
        'model': forms.CharField(),
        'account_id': forms.CharField(),
    })
    def delete(self, request, model, account_id, **kwargs):
        """
        重置密码
        :param request:
        :param model:
        :param account_id:
        :return:
        """
        if model == 'teacher':
            model_class = Teacher
        elif model == 'student':
            model_class = Student
        elif model == 'admin':
            model_class = Admin
        try:
            model_class.objects.get(pk=account_id)
            model_class.objects.filter(pk=account_id).update(psd=generate_md5('123456'))
            return response.correct_response()
        except model_class.DoesNotExist:
            return response.err_response_pk('account', account_id)


class ClazzListView(View):

    @verify_token(Admin)
    def get(self, request, **kwargs):
        classes = Clazz.objects.all()
        count = len(classes)
        if count == 0:
            return response.correct_response({
                'count': 0
            })
        attr_list = [
            'id',
            'name',
            'profession',
            ('students.all().count()', 'student_count')
        ]
        res = generate_dict_list(classes, attr_list)
        return response.correct_response({
            'count': count,
            'list': res,
        })

    @verify_token(Admin)
    @validate_args({
        'name': forms.CharField(max_length=30),
        'profession': forms.CharField(max_length=30)
    })
    def post(self, request, name, profession, **kwargs):
        Clazz.objects.create(name=name, profession=profession)
        return response.correct_response()


class AccountListView(View):

    @verify_token(Admin)
    @validate_args({
        'model': forms.CharField(),
    })
    def get(self, request, model, **kwargs):
        if model == 'teacher':
            model_class = Teacher
        elif model == 'student':
            model_class = Student
        elif model == 'admin':
            model_class = Admin
        accounts = model_class.objects.all()
        count = len(accounts)
        if count == 0:
            return response.correct_response({'count': 0})
        attr_list = [
            'num',
            'name',
        ]
        res = generate_dict_list(accounts, attr_list)
        return response.correct_response({'count': count, 'list': res})


class AccountDeleteView(View):
    @verify_token(Admin)
    @validate_args({
        'num': forms.CharField(),
        'model': forms.CharField(),
    })
    def delete(self, request, model, num, **kwargs):
        if model == 'teacher':
            model_class = Teacher
        elif model == 'student':
            model_class = Student
        elif model == 'admin':
            model_class = Admin
        model_class.objects.get(pk=num).delete()
        return response.correct_response()
