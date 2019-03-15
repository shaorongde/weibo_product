# Create your views here.
from django.shortcuts import render, redirect
from django.views import View

from api.models import User
from util.decorator import verify_token


class TokenDirectView(View):
    """
    验证token，直接通过
    """

    @verify_token()
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class StaticFileView(View):

    def get(self, request, *args, **kwargs):
        return redirect('/static' + request.path)

class RedirectView(View):
    """"
    需要重定向的路由
    """

    def get(self, request, **kwargs):
        role = request.COOKIES.get('role')
        if role == User.ROLE_STUDENT:
            return redirect('/student/')
        elif role == User.ROLE_TEACHER:
            return redirect('/teacher')
        elif role == User.ROLE_ADMIN:
            return redirect('/admin/')
        else:
            return redirect('/login/')


class NoTokenView(View):
    """
    直接通过的路由
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
