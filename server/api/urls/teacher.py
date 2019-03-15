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
from django.urls import path

from api.views.teacher import AccountView, LeaveListView, LeaveDetailView, ClassListView, MyClassListView, \
    MyClassManagementView, PsdView, StudentListView, StudentDetailView

urlpatterns = [
    path('account/', AccountView.as_view()),
    path('psd/', PsdView.as_view()),
    path('student/class/<int:clazz_id>/', StudentListView.as_view()),
    path('student/<str:num>/', StudentDetailView.as_view()),
    path('class/', ClassListView.as_view()),
    path('myclass/', MyClassListView.as_view()),
    path('myclass/<int:clazz_id>/', MyClassManagementView.as_view()),
    path('leave/', LeaveListView.as_view()),
    path('leave/<int:leave_id>/', LeaveDetailView.as_view()),
]
