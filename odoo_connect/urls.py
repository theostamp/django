# odoo_connect/urls

from django.urls import path
from . import views

urlpatterns = [
    path('odoo-products/', views.list_odoo_products, name='list_odoo_products'),
]

