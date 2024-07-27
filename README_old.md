

##  LOCAL ONLY ####
git fetch origin
git reset --hard origin/main
##




git init

git add .
git commit -m "update signup 8"
git branch -M main
git remote add origin https://github.com/theostamp/django.git
git push -u origin main 

git push -u origin main --force

cp .env.sample.devcontainer .env
python manage.py runserver 8003

chmod +x start1.sh
./start1.sh

python manage.py collectstatic 
python manage.py createsuperuser

  pip install -r requirements.txt

## To run the server, run the following command:

    python manage.py makemigrations  
    python manage.py makemigrations authentication
    python manage.py makemigrations admin
    python manage.py makemigrations tables
    python manage.py makemigrations tenants
    python manage.py makemigrations
    python manage.py makemigrations admin 


    python manage.py migrate
    python manage.py migrate tenants
    python manage.py migrate authentication   
    python manage.py migrate admin
    python manage.py migrate tables
    python manage.py migrate_schemas
    python manage.py migrate_schemas --shared 
     
  

    
python manage.py shell

from tenants.models import Tenant, Domain
from django.db import connection

# Δημιουργία ενός δημόσιου ενοικιαστή
tenant = Tenant(name='public_tenant', schema_name='public_tenant')
tenant.save()  # Αυτό θα δημιουργήσει επίσης το σχήμα της βάσης δεδομένων

# Ελέγξτε αν ο ενοικιαστής δημιουργήθηκε επιτυχώς
print(Tenant.objects.all())
from tenants.models import Tenant, Domain

# Ανακτήστε τον ενοικιαστή 'public_tenant'
public_tenant = Tenant.objects.get(name='public_tenant')

# Προσθέστε το domain 'localhost' στον ενοικιαστή 'public_tenant'
Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)

# Επαληθεύστε ότι το νέο domain προστέθηκε σωστά
print(Domain.objects.all())



    python manage.py runserver 8080



python manage.py createsuperuser    
python manage.py create_tenant
python manage.py create_tenant_superuser

python manage.py collectstatic

    daphne -u /tmp/daphne1.sock -b 0.0.0.0 -p 8003 rest_order.asgi:application    





docker system prune -a
docker image prune
docker volume prune

docker-compose logs -f



git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/theostamp/django.git
git push -u origin main 

git push -u origin main --force


Source directory     : /tmp/8dca0e8fedad367
Destination directory: cd /home/site/wwwroot





#εκτελεση στο theo.digns.net

  
python manage.py shell

from tenants.models import Tenant, Domain
from django.db import connection

# Δημιουργία ενός δημόσιου ενοικιαστή
tenant = Tenant(name='public_tenant', schema_name='public_tenant')
tenant.save()  # Αυτό θα δημιουργήσει επίσης το σχήμα της βάσης δεδομένων

# Ελέγξτε αν ο ενοικιαστής δημιουργήθηκε επιτυχώς
print(Tenant.objects.all())
from tenants.models import Tenant, Domain

# Ανακτήστε τον ενοικιαστή 'public_tenant'
public_tenant = Tenant.objects.get(name='public_tenant')

# Προσθέστε το domain 'theo.digns.net' στον ενοικιαστή 'public_tenant'
Domain.objects.create(domain='digns.net', tenant=public_tenant, is_primary=True)

# Επαληθεύστε ότι το νέο domain προστέθηκε σωστά
print(Domain.objects.all())



# Δημιουργία ενός δημόσιου ενοικιαστή
tenant = Tenant(name='public', schema_name='public')
tenant.save()  # Αυτό θα δημιουργήσει επίσης το σχήμα της βάσης δεδομένων

# Ελέγξτε αν ο ενοικιαστής δημιουργήθηκε επιτυχώς
print(Tenant.objects.all())
from tenants.models import Tenant, Domain

# Ανακτήστε τον ενοικιαστή 'public'
public = Tenant.objects.get(name='public')

# Προσθέστε το domain 'theo.digns.net' στον ενοικιαστή 'public'
Domain.objects.create(domain='digns.net', tenant=public, is_primary=True)

# Επαληθεύστε ότι το νέο domain προστέθηκε σωστά
print(Domain.objects.all())








# Δημιουργία ενός δημόσιου ενοικιαστή
tenant = Tenant(name='public', schema_name='public')
tenant.save()  # Αυτό θα δημιουργήσει επίσης το σχήμα της βάσης δεδομένων

# Ελέγξτε αν ο ενοικιαστής δημιουργήθηκε επιτυχώς
print(Tenant.objects.all())
from tenants.models import Tenant, Domain

# Ανακτήστε τον ενοικιαστή 'public'
public = Tenant.objects.get(name='public')

# Προσθέστε το domain 'theo.digns.net' στον ενοικιαστή 'public'
Domain.objects.create(domain='digns.net', tenant=public, is_primary=True)

# Επαληθεύστε ότι το νέο domain προστέθηκε σωστά
print(Domain.objects.all())



export PGHOST=dign-server.postgres.database.azure.com
export PGUSER=yylokmwbnf
export PGPORT=5432
export PGPASSWORD="theo663966@"
export PGDATABASE=postgres

    python manage.py migrate admin zero
    python manage.py migrate tenants zero
    
    python manage.py migrate tables zero
    python manage.py migrate_schemas zero
    python manage.py migrate_schemas --shared  zero
    





