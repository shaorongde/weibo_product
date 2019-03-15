import json
import copy
import collections
from django.shortcuts import render
from django.views.generic.base import View
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import EmptyPage, PageNotAnInteger
from .models import *
from django.db.models import Q
from .custom_paginator import CustomPaginator
from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    """
    登陆限定，并指定登陆url
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view, login_url='/users/login')


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        records = FHWModel.objects.all()
        current_page = request.GET.get("page", '1')
        paginator = CustomPaginator(current_page, 9, records, 6)
        try:
            paginator = paginator.page(current_page)  #获取前端传过来显示当前页的数据
        except PageNotAnInteger:
            # 如果有异常则显示第一页
            paginator = paginator.page(1)
        except EmptyPage:
            # 如果没有得到具体的分页内容的话,则显示最后一页
            paginator = paginator.page(paginator.num_pages)
        return render(request, 'index.html', {"paginator": paginator})

    def post(self, request):
        q = request.POST.get('q')
        movie_records = FHWModel.objects.all().filter(Q(title__icontains=q)| Q(content__icontains=q))
        current_page = request.GET.get("page", '1')
        paginator = CustomPaginator(current_page, 9, movie_records, 6)
        try:
            paginator = paginator.page(current_page)  #获取前端传过来显示当前页的数据
        except PageNotAnInteger:
            # 如果有异常则显示第一页
            paginator = paginator.page(1)
        except EmptyPage:
            # 如果没有得到具体的分页内容的话,则显示最后一页
            paginator = paginator.page(paginator.num_pages)
        return render(request, 'index.html', {"movie_records": movie_records, "paginator": paginator})


class KeywordsView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'keywords.html')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(KeywordsView, self).dispatch(*args, **kwargs)

    def post(self, request):
        _type = request.POST.get("type")
        # print(keyword)
        print('1-----',_type)
        # print(weight_count)
        print('1233',_type)
        TYPE_MAP = {"1": "myapp_fhwkeywordsmodel", "2": "myapp_zhihukeywordsmodel",
                    "3": "myapp_sinapaperskeywordsmodel", "4": "myapp_cctvxinwenkeywordsmodel"}
        with connection.cursor() as cursor:
            sql = "select keyword,weight_count from %s order by weight_count DESC limit 20 " % TYPE_MAP[_type]
            cursor.execute(sql)
            ret = cursor.fetchall()
            data = {"keyword": [], "weight_count": []}
            for item in ret:
                data["keyword"].append(item[0])
                data["weight_count"].append(item[1])
            return HttpResponse(json.dumps(data), content_type = 'application/json')
        
      
class RMRBFansView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'fans.html')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(RMRBFansView, self).dispatch(*args, **kwargs)

    def post(self, request):
        _type = request.POST.get("type")
        with connection.cursor() as cursor:
            if int(_type) == 1:
                sql = "select count(nickname),sex from myapp_fhwfansmodel group by sex"
                cursor.execute(sql)
                ret = cursor.fetchall()
                data = []
                for item in ret:
                    data.append({"name": item[1], "value": item[0]})
                return HttpResponse(json.dumps({"persent": data}), content_type = 'application/json')
            elif int(_type) == 2:
                sql = "select count(nickname),location from myapp_fhwfansmodel group by location " \
                      "ORDER by count(nickname) DESC limit 50"
                cursor.execute(sql)
                ret = cursor.fetchall()
                data = {"location": [], "count": []}
                for item in ret:
                    data["location"].append(item[1])
                    data["count"].append(item[0])
                return HttpResponse(json.dumps(data), content_type = 'application/json')


class SendCountView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'sended.html')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(SendCountView, self).dispatch(*args, **kwargs)

    def post(self, request):
        model_list = ["myapp_fhwmodel", "myapp_zhihumodel", "myapp_sinapapersmodel", "myapp_cctvxinwenmodel"]
        name_map = {"myapp_fhwmodel": "凤凰网", "myapp_zhihumodel": "知乎",
                    "myapp_sinapapersmodel": "新浪新闻", "myapp_cctvxinwenmodel": "CCTV新闻"}
        with connection.cursor() as cursor:
            data = []
            for item in model_list:
                sql = "select sum(send_count) from %s" % item
                cursor.execute(sql)
                ret = cursor.fetchone()
                for item2 in ret:
                    data.append({"name": name_map[item], "value": "%s" % item2})
            return HttpResponse(json.dumps({"persent": data}), content_type = 'application/json')




