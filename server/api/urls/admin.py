"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path

from api.views.admin import MyAccountView, ClazzListView, PsdView, ResetPsdView, InitView, AccountListView, \
    AccountDeleteView

urlpatterns = [
    path('account/', MyAccountView.as_view()),
    re_path(r'^account/(?P<model>(teacher)|(student)|(admin))/$', AccountListView.as_view()),
    re_path(r'^account/(?P<model>(teacher)|(student)|(admin))/(?P<num>\w+)/$', AccountDeleteView.as_view()),
    path('init/', InitView.as_view()),
    path('psd/', PsdView.as_view()),
    path('clazz/', ClazzListView.as_view()),
    re_path(r'^psd/(?P<model>(teacher)|(student)|(admin))/(?P<account_id>\w+)/$', ResetPsdView.as_view()),
]
