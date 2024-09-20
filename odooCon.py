import xmlrpc.client

# Στοιχεία σύνδεσης
ODOO_URL = 'https://oikonrg.odoo.com'  # Βασικό URL του instance
ODOO_DB = 'oikonrg'  # Όνομα βάσης δεδομένων
ODOO_USERNAME = 'theostam1966@gmail.com'  # Όνομα χρήστη
ODOO_PASSWORD = 'theo123@@@'  # Κωδικός πρόσβασης

# Σύνδεση με το Odoo
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

if uid:
    print(f"Authenticated as {ODOO_USERNAME} (UID: {uid})")
    
    # Δημιουργία συνδέσμου για τα models
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Παράδειγμα: Ανάκτηση προϊόντων από το Odoo
    products = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, 'product.product', 'search_read', [[]], 
        {'fields': ['name', 'list_price'], 'limit': 10}
    )

    # Εμφάνιση προϊόντων
    for product in products:
        print(f"Product: {product['name']} - Price: {product['list_price']}")
else:
    print("Authentication failed.")
