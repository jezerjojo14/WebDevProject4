from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    following=models.ManyToManyField("self", symmetrical=False)

class Post(models.Model):
    content=models.CharField(max_length=400)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    time=models.DateTimeField(default=timezone.now)
    edited=models.BooleanField(default=False)
    likes=models.ManyToManyField(User, related_name='likes')
