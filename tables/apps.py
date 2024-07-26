# tables\apps.py

from django.apps import AppConfig
import os
from django.conf import settings
import json

class TablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tables'

    def ready(self):
        tenants = ['theo']  # Προσθέστε εδώ όλους τους tenants που χρειάζεστε
        for tenant in tenants:
            tenant_folder = os.path.join(settings.BASE_DIR, 'tenants_folders', f'{tenant}_upload_json')
            received_orders_folder = os.path.join(settings.BASE_DIR, 'tenants_folders', f'{tenant}_received_orders')
            
            os.makedirs(tenant_folder, exist_ok=True)
            os.makedirs(received_orders_folder, exist_ok=True)

            # Δημιουργία κενών αρχείων JSON αν δεν υπάρχουν
            self.create_empty_json(os.path.join(tenant_folder, 'tables.json'), {"tables": []})
            self.create_empty_json(os.path.join(tenant_folder, 'products.json'), {"products": []})
            self.create_empty_json(os.path.join(tenant_folder, 'reservations.json'), {"reservations": []})
            self.create_empty_json(os.path.join(tenant_folder, 'occupied_tables.json'), {"tables": []})



    def create_empty_json(self, file_path, default_data):
        print(f"Checking file path: {file_path}")  # Προσθέστε αυτό για να δείτε τη διαδρομή
        if not os.path.exists(file_path):
            print(f"File not found, creating new file: {file_path}")
            with open(file_path, 'w') as file:
                json.dump(default_data, file, ensure_ascii=False, indent=4)
        else:
            print(f"File already exists: {file_path}") 