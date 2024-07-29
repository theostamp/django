
# authentication/models.py

from django.db import models
from django.utils import timezone
from tenants.models import Tenant  # Χρησιμοποιούμε το πλήρες μονοπάτι για να αποφύγουμε τον κυκλικό import
from django.contrib.auth.models import AbstractUser, Group, Permission


class LicenseKey(models.Model):
    key = models.CharField(max_length=32, unique=True)
    mac_address = models.CharField(max_length=17)
    hostname = models.CharField(max_length=255)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)  # Σύνδεση με τον Tenant
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key


class CustomUser(AbstractUser):
    restaurant_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set_permissions')

class Subscription(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)


