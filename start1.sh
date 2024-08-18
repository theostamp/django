#!/bin/bash
python3 -m pip install -r requirements.txt
python z_clear_cache.py
python z_clear.py

echo "Running migrations..."
python manage.py makemigrations authentication
python manage.py makemigrations  tables
python manage.py makemigrations
python manage.py migrate authentication --noinput || echo "Migrate authentication failed"
python manage.py migrate tables --noinput || echo "Migrate tables failed"
python manage.py migrate_schemas --noinput || echo "Migrate schemas failed"
python manage.py migrate --noinput || echo "Migrate failed"

echo "Creating public tenant and domain..."
python manage.py shell << END
from authentication.models import Tenant, Domain
from django.db import connection
import datetime

try:
    paid_until_date = datetime.date.today() + datetime.timedelta(days=365)  # 1 χρόνο από σήμερα

    tenant = Tenant(name='public_tenant', schema_name='public_tenant', paid_until=paid_until_date)
    tenant.save()
except Exception as e:
    print(f"Error creating tenant: {e}")

try:
    public_tenant = Tenant.objects.get(name='public_tenant')
    Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)
except Exception as e:
    print(f"Error creating domain: {e}")

try:
    tenant = Tenant(name='public', schema_name='public', paid_until=paid_until_date)
    tenant.save()
except Exception as e:
    print(f"Error creating tenant: {e}")

try:
    public = Tenant.objects.get(name='public')
    Domain.objects.create(domain='127.0.0.1', tenant=public, is_primary=True)
except Exception as e:
    print(f"Error creating domain: {e}")
END

python manage.py clearcache
echo "Starting server..."
cp .env.sample.devcontainer .env
python manage.py runserver 8003
python manage.py clearcache