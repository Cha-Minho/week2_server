# urls.py
from django.contrib import admin
from django.urls import path
from straight_neck_detector import views
from straight_neck_detector.login_view import *
from straight_neck_detector.posting_view import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', views.image_api, name='image_api'),
    path('register/', register_view, name = 'register'),
    path('login/', login_view, name = 'login'),
    path('test/', views.for_test),
    path('post/', posting),
    path('delete_post/', deleting),
    path('load_post/', load_post),
    path('edit_post/', edit_post),
    path('comment/', comment),
    path('load_comments/<int:post_id>/', load_comment),
    path('delete_comments/', delete_comment),
    path('search_post/', search_post),
    path('ur_name/', what_is_name),
]
