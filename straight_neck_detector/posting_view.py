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
from django.db.models import Q
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
    if request.method == 'POST':
        data = json.loads(request.body)
        post_id = data.get('postId')
        # try:
        post = Post.objects.get(id=post_id)
        post.delete()  # Delete the post
        return HttpResponse("Post deleted.")
        # except Post.DoesNotExist:
            # print("없다")
            # return HttpResponseBadRequest("Post does not exist.")
    else:
        return HttpResponseBadRequest("Only POST requests allowed.")


@csrf_exempt
def load_post(request):
    if request.method == "GET":
        posts = Post.objects.all()
        post_list = list(posts.values("id", "user_id", "title", "context", "date"))  # create a list of dict
        for post in post_list:
            post['date'] = post['date'].strftime("%m/%d %H:%M")
        post_list.reverse()
        return JsonResponse(post_list, safe=False)
    else:
        return HttpResponseBadRequest("Only Get Method is allowed.")



@csrf_exempt
def edit_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post_id = data.get('postId')
            title = data.get('title')
            content = data.get('content')
            print(post_id, title, content)
            post = Post.objects.get(id = post_id)

            post.title = title
            post.context = content
            post.save()

            return HttpResponse("Edit Complete.")
        except:
            return HttpResponseBadRequest("Edit Error.")
    else:
        return HttpResponseBadRequest("Only Post Method is Allowed.")
    
@csrf_exempt
def comment(request):
    print(request)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            context = data.get("context")
            post_id = data.get("post_id")
            print(post_id, user_id, context)
            user = User.objects.get(UserID = user_id)
            post = Post.objects.get(id = post_id)

            comment = Comment(post = post, user = user, context = context)
            comment.save()
            print(comment.id)
            return JsonResponse({'commentId': comment.id})
        except:
            return HttpResponseBadRequest("Commenting Error")
    else:
        print("Only POST requests allowed.")
        return HttpResponseBadRequest("Only POST requests allowed.")
    
@csrf_exempt
def load_comment(request, post_id):
    if request.method == 'GET':
        try:
            comments = Comment.objects.filter(post_id = post_id)
            comment_list = list(comments.values("id", "context", "date", "post_id", "user_id"))  # create a list of dict
            for comment in comment_list:
                comment['date'] = comment['date'].strftime("%m/%d %H:%M")
            print(post_id)
            return JsonResponse(comment_list, safe=False)
        except:
            return HttpResponseBadRequest("comment loading error.")
    else:
        HttpResponseBadRequest("Not a POST Method.")

@csrf_exempt
def delete_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        comment_id = data.get("commentId")
        comments = Comment.objects.get(id = comment_id)
        comments.delete()
        return HttpResponse("Comment delete complete")
    else:
        return HttpResponseBadRequest("Only GET method allowed")

@csrf_exempt
def search_post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        search_query = data.get("searchQuery")
        if search_query:
            posts = Post.objects.filter(Q(title__icontains=search_query) | Q(context__icontains=search_query))
            post_list = list(posts.values("id", "user_id", "title", "context", "date"))  # create a list of dict
            for post in post_list:
                context = post['context']
                post['date'] = post['date'].strftime("%m/%d %H:%M")
                if len(context) > 50 or context.count('\n') > 1:
                    if context.count('\n') > 1:
                        context = '\n'.join(context.split('\n')[:2])  # limit to first 3 lines
                    else:
                        context = context[:50]  # limit to first 50 characters
                    context += '...'  # add ellipsis
                    post['context'] = context  # update the post's context
            post_list.reverse()
            return JsonResponse(post_list, safe=False)
        else:
            return HttpResponseBadRequest("Search query is empty.")
    else:
        return HttpResponseBadRequest("Only POST requests allowed.")