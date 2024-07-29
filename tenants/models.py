# tenants/models.py

from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

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
