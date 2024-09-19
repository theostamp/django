from django.shortcuts import render
from .models import Payment, Invoice, Sale, Product

def list_payments(request):
    tenant = request.tenant  # Ανάκτηση του tenant από το request
    payments = Payment.objects.filter(tenant=tenant)
    return render(request, 'odoo_connect/payments.html', {'payments': payments})

def list_invoices(request):
    tenant = request.tenant
    invoices = Invoice.objects.filter(tenant=tenant)
    return render(request, 'odoo_connect/invoices.html', {'invoices': invoices})

def list_sales(request):
    tenant = request.tenant
    sales = Sale.objects.filter(tenant=tenant)
    return render(request, 'odoo_connect/sales.html', {'sales': sales})

def list_products(request):
    tenant = request.tenant
    products = Product.objects.filter(tenant=tenant)
    return render(request, 'odoo_connect/products.html', {'products': products})
