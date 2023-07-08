# models.py
from django.db import models

class Image(models.Model):
    image = models.ImageField(upload_to='images/')

class users(models.Model):
    email = models.EmailField(verbose_name='email', max_length=255, unique=True, primary_key=True)
    password = models.CharField(verbose_name='password', max_length=255)
    name = models.CharField(max_length=255)
    is_employed = models.BooleanField(default= False)

    class Meta:
        db_table = 'users'
