from django.contrib.auth.models import AbstractUser
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    subscription_type = models.CharField(max_length=50, blank=True, null=True)  # Προσθήκη του πεδίου subscription_type

class Domain(DomainMixin):
    pass

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)  # Σιγουρευτείτε ότι το email είναι υποχρεωτικό και μοναδικό

class Subscription(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=False)
    temporary_key = models.CharField(max_length=8, blank=True, null=True)

class License(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    license_key = models.CharField(max_length=255, unique=True)
    hardware_id = models.CharField(max_length=255)
    computer_name = models.CharField(max_length=255)
    expiration_date = models.DateField()
    active = models.BooleanField(default=False)
