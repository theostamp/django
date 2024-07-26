
# authentication/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    restaurant_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set_permissions')
