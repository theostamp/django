# tenants/admin.py

from django.contrib import admin
from .models import Tenant, Domain

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'created_on')
    search_fields = ('name', 'schema_name')
    list_filter = ('created_on',)
    ordering = ('name',)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant')
    search_fields = ('domain', 'tenant__name')  # Η διπλή υπογράμμιση χρησιμοποιείται για την πρόσβαση σε σχετικά πεδία
    list_filter = ('tenant__name',)
    ordering = ('domain',)
