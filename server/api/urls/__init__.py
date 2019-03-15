from django.urls import path, include

urlpatterns = [
    path('student/', include('api.urls.student')),
    path('teacher/', include('api.urls.teacher')),
    path('admin/', include('api.urls.admin')),
]
