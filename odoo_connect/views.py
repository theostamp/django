from django.shortcuts import render
import xmlrpc.client

# Στοιχεία σύνδεσης
ODOO_URL = 'https://oikonrg.odoo.com'
ODOO_DB = 'oikonrg'
ODOO_USERNAME = 'theostam1966@gmail.com'
ODOO_PASSWORD = 'theo123@@@'

def list_odoo_products(request):
    # Σύνδεση με το Odoo
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

    if uid:
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', [[]], {'fields': ['name', 'list_price'], 'limit': 10})
        
        return render(request, 'odoo_connect/product_list.html', {'products': products})
    else:
        return render(request, 'odoo_connect/error.html', {'message': 'Authentication failed'})
