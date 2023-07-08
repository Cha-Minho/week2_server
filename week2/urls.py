# urls.py
from django.contrib import admin
from django.urls import path
from straight_neck_detector import views
from straight_neck_detector.login_view import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', views.image_api, name='image_api'),
    path('register/', register_view, name = 'register'),
    path('login/', login_view, name = 'login')
]
