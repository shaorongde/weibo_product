from django.db import models
from util.my_md5 import generate_md5


# Create your models here.
class User(models.Model):
    ROLE_STUDENT = 0
    ROLE_TEACHER = 1
    ROLE_ADMIN = 2

    """
    所有用户类的抽象类
    """

    class Meta:
        abstract = True

    num = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=15, default='')
    psd = models.CharField(max_length=32)
    token = models.CharField(max_length=42, default='')

    def update_token(self):
        from util import my_token
        self.token = my_token.generate_token(self.num)
        self.__class__.objects.filter(
            pk=self.num, psd=self.psd
        ).update(token=self.token)
        return self.token


class Student(User):
    class Meta:
        db_table = 'student'

    sex = models.CharField(max_length=2, default='男')
    nation = models.CharField(max_length=100, default='')  # 民族
    politics_status = models.CharField(max_length=100, default='')  # 政治面貌
    huji = models.CharField(max_length=100, default='')  # 户籍类型
    origin = models.CharField(max_length=100, default='')  # 生源地
    address = models.CharField(max_length=100, default='')  # 家庭住址
    id = models.CharField(max_length=18, default='')  # 身份证号
    tele = models.CharField(max_length=11, default='')  # 电话
    email = models.CharField(max_length=100, default='')  # email

    birth = models.DateField(auto_now_add=True)
    date_in_school = models.DateField(auto_now_add=True)

    chidao = models.IntegerField(default=0)
    zaotui = models.IntegerField(default=0)
    chufen = models.IntegerField(default=0)

    clazz = models.ForeignKey(to='Clazz', related_name='students', on_delete=models.CASCADE)


class Teacher(User):
    class Meta:
        db_table = 'teacher'

    sex = models.CharField(max_length=2, default='男')
    nation = models.CharField(max_length=20, default='')  # 民族
    politics_status = models.CharField(max_length=15, default='')  # 政治面貌
    huji = models.CharField(max_length=15, default='')  # 户籍类型
    origin = models.CharField(max_length=40, default='')  # 生源地
    address = models.CharField(max_length=50, default='')  # 家庭住址
    id = models.CharField(max_length=18, default='')  # 身份证号
    tele = models.CharField(max_length=11, default='')  # 电话
    email = models.CharField(max_length=30, default='')  # email


class Clazz(models.Model):
    class Meta:
        db_table = 'class'

    name = models.CharField(max_length=30, default='')
    profession = models.CharField(max_length=30, default='')

    teacher = models.ForeignKey(to='Teacher', related_name='classes', on_delete=models.CASCADE, null=True)


class Leave(models.Model):
    """
    请假记录
    """

    STATE_WAITING = 0
    STATE_YES = 1
    STATE_NO = 2

    class Meta:
        db_table = 'leave'
        ordering = ['-created_time', '-date']

    reason = models.CharField(max_length=100, default='')
    date = models.DateField()
    created_time = models.DateTimeField(auto_now_add=True)
    state = models.IntegerField(default=STATE_WAITING)

    student = models.ForeignKey(to='Student', related_name='leaves', on_delete=models.CASCADE)


class Admin(User):
    class Meta:
        db_table = 'admin'
