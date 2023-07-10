from django.views.decorators.csrf import csrf_exempt
from .forms import ImageUploadForm
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from PIL import Image
from io import BytesIO
import time
import math as m
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from django.conf import settings
from django.db import connection
from .models import Post, Comment, User
import json

@csrf_exempt
def posting(request):
    print(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get("userId")
        title = data.get("postTitle")
        context = data.get("postContent")

        if user_id and User.objects.filter(UserID = user_id).exists():
            user = User.objects.get(UserID = user_id)
            posting = Post(user = user, title = title, context = context)
            posting.save()
            return HttpResponse("Posting Success")
        else:
            print("NO such user.")
            return HttpResponseBadRequest("NO SUCH USER.")
    else:
        print("Only POST requests allowed.")
        return HttpResponseBadRequest("Only POST requests allowed.")

@csrf_exempt
def deleting(request):
    return HttpResponse("아직 안 만듦 ㅎㅎ;;")

@csrf_exempt
def load_post(request):
    if request.method == "GET":
            posts = Post.objects.all()
            post_list = list(posts.values("user__email", "title", "context", "date"))  # create a list of dict
            return JsonResponse(post_list, safe=False)
    else:
        return HttpResponseBadRequest("Only Get Method is allowed.")