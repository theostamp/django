from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    name = models.CharField(max_length=100, unique=True)
    created_on = models.DateField(auto_now_add=True)
    # Προσθέστε εδώ άλλα πεδία αν χρειάζεται

    auto_drop_schema = True
    auto_create_schema = True

    def save(self, *args, **kwargs):
        super(Tenant, self).save(*args, **kwargs)
        domain_name = f"{self.name}.localhost"
        if not Domain.objects.filter(domain=domain_name).exists():
            Domain.objects.create(domain=domain_name, tenant=self, is_primary=True)

class Domain(DomainMixin):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    # Μπορείτε να προσθέσετε επιπλέον πεδία εδώ αν χρειάζεται

class Subscription(models.Model):
    SUBSCRIPTION_TYPES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    subscription_type = models.CharField(max_length=100, choices=SUBSCRIPTION_TYPES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # ...

    def __str__(self):
        return f"Subscription for {self.tenant.name} [{self.subscription_type}]"
