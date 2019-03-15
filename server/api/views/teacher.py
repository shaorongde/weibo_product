from django import forms
from django.views import View

# Create your views here.
from api.models import Teacher, Clazz, Leave, User, Student
from api.service.account import modify_psd
from util import response
from util.decorator import validate_args, fetch_object, verify_token
from util.normal import generate_dict_from_object, generate_dict_from_dict, generate_dict_list


class AccountView(View):

    @validate_args({
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
            user = Teacher.objects.get(pk=num, psd=psd)
            token = user.update_token()
            res = response.correct_response()
            res.set_cookie('TOKEN', token)
            res.set_cookie('role', User.ROLE_TEACHER)
            return res
        except Teacher.DoesNotExist:
            return response.err_response(1)

    @validate_args({
        'num': forms.CharField(max_length=15, min_length=1),
        'psd': forms.CharField(max_length=32, min_length=32),
        'name': forms.CharField(max_length=20),
    })
    def post(self, request, num, psd, name, **kwargs):
        """
        注册
        :param request:
        :return:
        """
        try:
            Teacher.objects.get(pk=num)
            return response.err_response(1)
        except Teacher.DoesNotExist:
            Teacher.objects.create(num=num, psd=psd, name=name)
            return response.correct_response()


class PsdView(View):

    @verify_token(Teacher)
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
        """
        result = modify_psd(Teacher, me, old, new)
        if result:
            return response.correct_response()
        else:
            return response.err_response(1)


class InfoView(View):

    @verify_token(Teacher)
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
        ]
        res = generate_dict_from_object(me, attr_list)
        return response.correct_response(res)

    @verify_token(Teacher)
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
        修改信息
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
        Teacher.objects.filter(pk=me.num).update(**update_params)
        return response.correct_response()


class ClassListView(View):

    @verify_token(Teacher)
    def get(self, request, me):
        """
        获取允许添加班主任的班级
        :param request:
        :param me:
        :return:
        """
        classes = Clazz.objects.filter(teacher__isnull=True)
        count = len(classes)
        if count == 0:
            return response.correct_response({'count': 0})
        attr_list = [
            'id',
            'name',
            'profession',
            ('students.all().count()', 'student_count'),
        ]
        res = generate_dict_list(classes, attr_list)
        return response.correct_response({'count': count, 'list': res})


class MyClassListView(View):

    @verify_token(Teacher)
    def get(self, request, me):
        """
        老师获取自己管理的班级
        :param request:
        :return:
        name 班级名称
        profession 所属专业
        student_count 班级人数
        """
        classes = me.classes.all()
        count = len(classes)
        if count == 0:
            return response.correct_response({'count': 0})
        attr_list = [
            'id',
            'name',
            'profession',
            ('students.all().count()', 'student_count'),
        ]
        res = generate_dict_list(classes, attr_list)
        return response.correct_response({'count': count, 'list': res})


class MyClassManagementView(View):
    @verify_token(Teacher)
    @validate_args({
        'clazz_id': forms.IntegerField(),
    })
    @fetch_object(Clazz, 'clazz')
    def post(self, request, clazz, me):
        """
        老师添加自己管理的班级
        :param request:
        :param clazz:
        :param me:
        :return:
        错误code
        1，班级已经有班主任
        """
        if clazz.teacher is not None:
            return response.err_response(1)
        else:
            me.classes.add(clazz)
            return response.correct_response()

    @verify_token(Teacher)
    @validate_args({
        'clazz_id': forms.IntegerField(),
    })
    @fetch_object(Clazz, 'clazz')
    def delete(self, request, me, clazz):
        """
        老师减少自己管理的班级
        :param request:
        :param me:
        :param clazz:
        :return:
        """
        if clazz.teacher.num == me.num:
            me.classes.remove(clazz)
            return response.correct_response()
        else:
            return response.err_response_not_belong('teacher', me.num, 'class', clazz.id)


class StudentListView(View):
    @verify_token(Teacher)
    @validate_args({
        'clazz_id': forms.IntegerField(),
    })
    @fetch_object(Clazz, 'clazz')
    def get(self, request, me, clazz):
        students = clazz.students.all()
        count = len(students)
        if count == 0:
            return response.correct_response({'count': 0})
        attr_list = [
            'name',
            'num',
            'sex',
            'chidao',
            'zaotui',
            'chufen',
        ]
        res = generate_dict_list(students, attr_list)
        return response.correct_response({'count': count, 'list': res})


class StudentDetailView(View):

    @verify_token(Teacher)
    @validate_args({
        'num': forms.CharField(),
    })
    @fetch_object(Student, 'student', 'num')
    def get(self, request, student, **kwargs):
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
            'chidao',
            'zaotui',
            'chufen',
        ]
        res = generate_dict_from_object(student, attr_list)
        return response.correct_response(res)

    @verify_token(Teacher)
    @validate_args({
        'num':forms.CharField(max_length=15),
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
        'chidao': forms.IntegerField(required=False),
        'zaotui': forms.IntegerField(required=False),
        'chufen': forms.IntegerField(required=False),
    })
    @fetch_object(Student, 'student', 'num')
    def post(self, request, student, **kwargs):
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
            'chidao',
            'zaotui',
            'chufen',
            'date_in_school',
        ]
        update_params = generate_dict_from_dict(kwargs, attr_list, False)
        if len(update_params) == 0:
            return response.correct_response()
        Student.objects.filter(pk=student.num).update(**update_params)
        return response.correct_response()

    @verify_token(Teacher)
    @validate_args({
        'num': forms.CharField(),
    })
    @fetch_object(Student, 'student', 'num')
    def delete(self, request, student, **kwargs):
        student.delete()
        return response.correct_response()


class LeaveListView(View):

    @verify_token(Teacher)
    def get(self, request, me):
        """
        获取老师所带班级的所有请假申请
        :param request:
        :param me:
        :return:
        """
        leaves = Leave.objects.filter(student__clazz__teacher=me)
        count = len(leaves)
        if count == 0:
            return response.correct_response({'count': 0})
        attr_list = [
            'id',
            'date',
            'reason',
            'state',
            'student.name',
            ('student.clazz.name', 'class_name'),
        ]
        res = generate_dict_list(leaves, attr_list)
        return response.correct_response({'count': count, 'list': res})


class LeaveDetailView(View):

    @verify_token(Teacher)
    @validate_args({
        'leave_id': forms.IntegerField(),
        'allow': forms.BooleanField(required=False),
    })
    @fetch_object(Leave, 'leave')
    def post(self, request, me, leave, allow=False):
        """
        审核请假
        :param request:
        :param me:
        :return:
        错误code
        1，该请假申请已审核，不能修改
        """
        if leave.state != Leave.STATE_WAITING:
            return response.err_response(1)
        if leave.student.clazz.teacher.num == me.num:
            if allow:
                Leave.objects.filter(pk=leave.id).update(state=Leave.STATE_YES)
            else:
                Leave.objects.filter(pk=leave.id).update(state=Leave.STATE_NO)
            return response.correct_response()
        else:
            return response.err_response_not_belong('teacher', me.num, 'leave', leave.id)
