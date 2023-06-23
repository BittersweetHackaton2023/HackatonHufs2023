from django.contrib.auth.models import AbstractUser
from django.db import models



class Member(models.Model):
    email = models.EmailField(unique=True)
    mileage = models.IntegerField(default=0)
