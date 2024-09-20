from django.db import models
from django_tenants.models import TenantMixin
from authentication.models import Tenant  # Αναφέρεται το μοντέλο Tenant που ήδη έχεις δημιουργήσει

class Product(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)  # Συσχετίζουμε το προϊόν με τον tenant
    product_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)  # Συσχέτιση με τον tenant
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount}"

class Invoice(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)  # Συσχέτιση με τον tenant
    invoice_id = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issue_date = models.DateField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Invoice {self.invoice_id} - {self.customer_name}"

class Sale(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)  # Συσχέτιση με τον tenant
    sale_id = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale {self.sale_id} - {self.product.name} ({self.quantity})"

