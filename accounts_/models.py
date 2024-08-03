from django.contrib.auth.models import AbstractUser
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    # Προσθήκη επιπλέον πεδίων, εάν απαιτείται
    pass

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

class Subscription(models.Model):
    SUBSCRIPTION_TYPES = (
        ('trial', 'One Month Trial'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    subscription_type = models.CharField(max_length=100, choices=SUBSCRIPTION_TYPES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Subscription for {self.tenant.name} [{self.subscription_type}]"


from django.utils import timezone

class License(models.Model):
    tenant = models.OneToOneField('Tenant', on_delete=models.CASCADE)
    license_key = models.CharField(max_length=255, unique=True)
    hardware_id = models.CharField(max_length=255)
    expiration_date = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Χωρίς default
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"License for {self.tenant.schema_name}"




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

class Order(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
