import os
import uuid
from datetime import timedelta
from django.utils import timezone
from authentication.models import Subscription, License

# Ορισμός του αρχείου ρυθμίσεων του Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'azureproject.settings')
import django
django.setup()

temporary_key = "62184540"
subscription = Subscription.objects.get(temporary_key__iexact=temporary_key)

if subscription.active:
    tenant = subscription.tenant
    permanent_key = str(uuid.uuid4())
    expiration_date = timezone.now().date() + timedelta(days=30)

    license, created = License.objects.get_or_create(
        tenant=tenant,
        defaults={
            'license_key': permanent_key,
            'expiration_date': expiration_date,
            'active': True,
            'hardware_id': '',
            'computer_name': '',
        }
    )

    if not created:
        license.license_key = permanent_key
        license.expiration_date = expiration_date
        license.active = True
        license.save()

    print(f"License created with permanent_key: {permanent_key}")
else:
    print("Subscription is not active.")
