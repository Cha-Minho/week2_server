# models.py
from django.db import models

class User(models.Model):
    UserID = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    is_employed = models.BooleanField()

    def __str__(self):
        return self.email

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    context = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    context = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.context