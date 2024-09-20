from django.shortcuts import render
from .models import Product
import xmlrpc.client

# Στοιχεία σύνδεσης
ODOO_URL = 'https://oikonrg.odoo.com'
ODOO_DB = 'oikonrg'
ODOO_USERNAME = 'theostam1966@gmail.com'
ODOO_PASSWORD = 'theo123@@@'

def sync_odoo_products(request):
    tenant = request.tenant  # Ανάκτηση του tenant από το request
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

    if uid:
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', [[]], {'fields': ['name', 'list_price'], 'limit': 10})

        # Αποθήκευση των προϊόντων στη βάση δεδομένων για τον συγκεκριμένο tenant
        for product in products:
            Product.objects.update_or_create(
                product_id=product['id'],
                tenant=tenant,  # Αποθήκευση με τον σωστό tenant
                defaults={
                    'name': product['name'],
                    'price': product['list_price'],
                    'stock': 0  # Προσαρμόστε ανάλογα με τις ανάγκες
                }
            )
        return render(request, 'odoo_connect/sync_success.html')
    else:
        return render(request, 'odoo_connect/error.html', {'message': 'Authentication failed'})


def list_products(request):
    tenant = request.tenant  # Ανάκτηση του tenant από το request
    products = Product.objects.filter(tenant=tenant)  # Φιλτράρισμα προϊόντων για τον συγκεκριμένο tenant
    
    return render(request, 'odoo_connect/product_list.html', {'products': products})


def create_odoo_product_for_tenant(tenant, product_data):
    # Σύνδεση με το Odoo
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    
    if uid:
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        # Προσθήκη προϊόντος με tenant_id
        product_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'create', [{
            'name': product_data['name'],
            'list_price': product_data['price'],
            'tenant_id': tenant.id  # Προσθήκη του tenant_id
        }])
        return product_id
    else:
        raise Exception("Failed to authenticate with Odoo")


def create_odoo_invoice_for_tenant(tenant, invoice_data):
    # Σύνδεση με το Odoo
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    
    if uid:
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        # Δημιουργία τιμολογίου με tenant_id
        invoice_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'account.move', 'create', [{
            'move_type': 'out_invoice',  # Τύπος τιμολογίου
            'partner_id': invoice_data['partner_id'],  # Πελάτης
            'invoice_date': invoice_data['date'],  # Ημερομηνία
            'tenant_id': tenant.id,  # Προσθήκη του tenant_id
            'invoice_line_ids': [(0, 0, {
                'product_id': invoice_data['product_id'],
                'quantity': invoice_data['quantity'],
                'price_unit': invoice_data['price'],
            })]
        }])
        return invoice_id
    else:
        raise Exception("Failed to authenticate with Odoo")

# def send_invoice_to_provider(invoice_data):
#     # Υποθετική κλήση στον πάροχο τιμολόγησης
#     response = requests.post("https://provider.example.com/api/invoice", json=invoice_data)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         raise Exception("Failed to send invoice")
