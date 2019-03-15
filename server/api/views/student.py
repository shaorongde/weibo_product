from django import forms
from django.views import View

# Create your views here.
from api.models import Student, Clazz, Leave, User
from api.service.account import modify_psd
from util import response
from util.decorator import validate_args, fetch_object, verify_token
from util.normal import generate_dict_from_object, generate_dict_from_dict, generate_dict_list


class AccountView(View):

    @validate_args({#进行输入数据验证
        'num': forms.CharField(max_length=15),
        'psd': forms.CharField(max_length=32, min_length=32),
    })
    def get(self, request, num, psd):
        """
        登录
        :param request:
        :return:
        错误code
        1：账号或密码错误
        """
        try:
            user = Student.objects.get(pk=num, psd=psd)
            token = user.update_token()
            res = response.correct_response()
            res.set_cookie('TOKEN', token)
            res.set_cookie('role', User.ROLE_STUDENT)
            return res
        except Student.DoesNotExist:
            return response.err_response(1)

    @validate_args({#进行输入数据验证
        'num': forms.CharField(max_length=15, min_length=1),
        'psd': forms.CharField(max_length=32, min_length=32),
        'name': forms.CharField(max_length=20),
        'clazz_id': forms.IntegerField(),
    })
    @fetch_object(Clazz, 'clazz')
    def post(self, request, num, psd, name, clazz, **kwargs):
        """
        注册
        :param request:
        :return:
        错误code
        1,学号已存在
        """
        try:
            Student.objects.get(pk=num)
            return response.err_response(1)
        except Student.DoesNotExist:
            Student.objects.create(num=num, psd=psd, name=name, clazz=clazz)
            return response.correct_response()


class InfoView(View):

    @verify_token(Student)
    def get(self, request, me):
        """
        查看信息
        :param request:
        :param me:
        :return:
        """
        attr_list = [
            'num',
            'id',
            'name',
            'sex',
            'politics_status',
            'huji',
            'nation',
            'origin',
            'tele',
            'email',
            'birth',
            'date_in_school',
            'clazz.name',
            'clazz.profession',
        ]
        res = generate_dict_from_object(me, attr_list)
        return response.correct_response(res)

    @verify_token(Student)
    @validate_args({
        'id': forms.CharField(max_length=18, min_length=18, required=False),
        'name': forms.CharField(max_length=15, required=False),
        'sex': forms.CharField(max_length=2, required=False),
        'politics_status': forms.CharField(max_length=100, required=False),
        'huji': forms.CharField(max_length=100, required=False),
        'nation': forms.CharField(max_length=100, required=False),
        'origin': forms.CharField(max_length=100, required=False),
        'tele': forms.CharField(max_length=11, required=False),
        'email': forms.CharField(max_length=100, required=False),
        'birth': forms.DateField(required=False),
        'date_in_school': forms.DateField(required=False),
    })
    def post(self, request, me, **kwargs):
        """
        修改信息，只传需要修改的信息
        :param request:
        :param me:
        :return:
        """
        attr_list = [
            'id',
            'name',
            'sex',
            'politics_status',
            'huji',
            'nation',
            'origin',
            'tele',
            'email',
            'birth',
            'date_in_school',
        ]
        update_params = generate_dict_from_dict(kwargs, attr_list, False)
        if len(update_params) == 0:
            return response.correct_response()
        Student.objects.filter(pk=me.num).update(**update_params)
        return response.correct_response()


class PsdView(View):

    @verify_token(Student)
    @validate_args({
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
        result = modify_psd(Student, me, old, new)
        if result:
            return response.correct_response()
        else:
            return response.err_response(1)


class AttendanceView(View):

    @verify_token(Student)
    def get(self, request, me):
        res = {
            'chidao': me.chidao,
            'zaotui': me.zaotui,
            'chufen': me.chufen,
        }
        return response.correct_response(res)


class ClazzListView(View):

    def get(self, request, **kwargs):
        """
        获取能够加入的班级
        :param request:
        :param kwargs:
        :return:
        """
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
        ]
        res = generate_dict_list(classes, attr_list)
        return response.correct_response({
            'count': count,
            'list': res,
        })


class LeaveListView(View):

    @verify_token(Student)
    def get(self, request, me):
        """
        获取我的请假申请
        :param request:
        :param me:
        :return:
        """
        leaves = me.leaves.all()
        count = len(leaves)
        if count == 0:
            return response.correct_response({'count': 0})
        attr_list = [
            'date',
            'reason',
            'state',
        ]
        res = generate_dict_list(leaves, attr_list)
        return response.correct_response({'count': count, 'list': res})

    @verify_token(Student)
    @validate_args({
        'reason': forms.CharField(max_length=100),
        'date': forms.DateField(),
    })
    def post(self, request, me, reason, date):
        """
        请假申请
        :param request:
        :param me:
        :param reason:
        :param date:
        :return:
        """
        Leave.objects.create(reason=reason, date=date, student=me)
        return response.correct_response()


class LeaveDetailView(View):

    @verify_token(Student)
    @validate_args({
        'leave_id': forms.IntegerField(),
    })
    @fetch_object(Leave, 'leave')#在执行view函数前提前取出某个模型实例
    def delete(self, request, me, leave):
        """
        删除请假申请
        :param request:
        :param me:
        :return:
        """
        if leave.student.num == me.num:
            leave.delete()
            return response.correct_response()
        else:
            return response.err_response_not_belong('student', me.num, 'leave', leave.id)
