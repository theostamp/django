# tables/admin.py

from django.contrib import admin
from .models import Product, Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1  # Προσαρμόστε αναλόγως

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('category', 'description', 'price', 'amount')
    list_filter = ('category',)
    search_fields = ('description',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'timestamp', 'waiter', 'order_done', 'printed', 'order_id')
    list_filter = ('waiter', 'order_done')
    search_fields = ('order_id', 'table_number')
    inlines = [OrderProductInline]

# Επιλογή να μην εγγράψετε το OrderProduct στο admin ως αυτόνομη ενότητα, αλλά μόνο μέσω των inlines του Order
# admin.site.register(OrderProduct)
