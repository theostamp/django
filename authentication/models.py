from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone

class CustomUser(AbstractUser):
    restaurant_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set_permissions')

class Tenant(TenantMixin):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateField(auto_now_add=True)
    subscription_type = models.CharField(max_length=100)

    auto_drop_schema = True
    auto_create_schema = True

    def save(self, *args, **kwargs):
        super(Tenant, self).save(*args, **kwargs)
        domain_name = f"{self.name}.localhost"
        if not Domain.objects.filter(domain=domain_name).exists():
            Domain.objects.create(domain=domain_name, tenant=self, is_primary=True)

class Domain(DomainMixin):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)




# models.py
from django.db import models

class Subscription(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=False)
    temporary_key = models.CharField(max_length=8, blank=True, null=True)  # Προσθήκη του πεδίου temporary_key

    def __str__(self):
        return f'{self.tenant.name} - {self.subscription_type}'




class License(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    license_key = models.CharField(max_length=100, unique=True)
    hardware_id = models.CharField(max_length=100)
    computer_name = models.CharField(max_length=100)  # Προσωρινή default τιμή
    # computer_name = models.CharField(max_length=100, default='TemporaryName')  # Προσωρινή default τιμή
    expiration_date = models.DateField()
    active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.tenant.name} - {self.license_key}"

class TemporaryKey(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=255)
    key = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)
