#!/bin/bash
python3 -m pip install -r requirements.txt
echo "Running migrations..."
python manage.py makemigrations authentication
python manage.py makemigrations restaurant_review
python manage.py makemigrations tenants
python manage.py makemigrations
python manage.py migrate tenants --noinput || echo "Migrate tenants failed"
python manage.py migrate authentication --noinput || echo "Migrate authentication failed"
python manage.py migrate restaurant_review --noinput || echo "Migrate restaurant_review failed"
python manage.py migrate_schemas --noinput || echo "Migrate schemas failed"
python manage.py migrate --noinput || echo "Migrate failed"

echo "Creating public tenant and domain..."
python manage.py shell << END
from tenants.models import Tenant, Domain
from django.db import connection

try:
    tenant = Tenant(name='public_tenant', schema_name='public_tenant')
    tenant.save()
except Exception as e:
    print(f"Error creating tenant: {e}")

try:
    public_tenant = Tenant.objects.get(name='public_tenant')
    Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)
except Exception as e:
    print(f"Error creating domain: {e}")



try:
    tenant = Tenant(name='public', schema_name='public')
    tenant.save()
except Exception as e:
    print(f"Error creating tenant: {e}")

try:
    public = Tenant.objects.get(name='public')
    Domain.objects.create(domain='127.0.0.1', tenant=public, is_primary=True)
except Exception as e:
    print(f"Error creating domain: {e}")


END





echo "Starting  server..."
# gunicorn --workers 2 --threads 4 --timeout 60 --access-logfile '-' --error-logfile '-' --bind=0.0.0.0:8000 --chdir=/home/site/wwwroot azureproject.wsgi
  cp .env.sample.devcontainer .env
  python manage.py runserver 8003