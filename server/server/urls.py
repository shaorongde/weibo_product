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
from django.urls import path, include, re_path

from router.views import TokenDirectView, NoTokenView, RedirectView, StaticFileView

urlpatterns = [
    path('api/', include('api.urls')),
    re_path(r'^(student)|(teacher)|(admin)/', TokenDirectView.as_view()),
    re_path(r'^(login)|(signup)/$', NoTokenView.as_view()),
    re_path(r'^.+(\..+)$', StaticFileView.as_view()),
    path('', RedirectView.as_view()),
]
