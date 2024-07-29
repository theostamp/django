
# tenants/views.py


from django.shortcuts import render, redirect
from .models import Tenant  # Υποθέτοντας ότι το μοντέλο του tenant είναι Tenant
from .forms import SubscriptionForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tenants.models import Tenant, Subscription
from django.shortcuts import render, redirect
from tenants.models import Tenant, Subscription, License
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Tenant, Subscription, License
import uuid

@login_required
def profile_view(request):
    current_user = request.user
    tenant = None
    subscription = None

    try:
        tenant = Tenant.objects.get(schema_name=current_user.username)
        subscription = Subscription.objects.get(tenant=tenant)
    except Tenant.DoesNotExist:
        pass
    except Subscription.DoesNotExist:
        pass

    context = {
        'current_user': current_user,
        'tenant': tenant,
        'subscription': subscription,
    }

    return render(request, 'tenants/profile.html', context)

from django_tenants.middleware.main import TenantMainMiddleware

class CustomTenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, model, hostname, request):
        try:
            return super().get_tenant(model, hostname, request)
        except model.DoesNotExist:
            return model.objects.get(schema_name='public')  # ή ορίστε κάποιον άλλο default tenant

@csrf_exempt
def generate_temporary_key(request):
    # Η συνάρτηση αυτή καλείται μετά την επιβεβαίωση πληρωμής
    user = request.user
    temporary_key = str(uuid.uuid4())
    # Αποθηκεύστε το προσωρινό κλειδί και τη λήξη του στη βάση δεδομένων ή σε cache
    return JsonResponse({"temporary_key": temporary_key})

@csrf_exempt
def activate_license(request):
    temporary_key = request.POST.get('temporary_key')
    hardware_id = request.POST.get('hardware_id')
    computer_name = request.POST.get('computer_name')

    # Επικυρώστε το προσωρινό κλειδί (λογική επικύρωσης)
    user = request.user  # Λάβετε τον χρήστη που κάνει την αίτηση
    tenant = Tenant.objects.get(schema_name=user.username)

    # Δημιουργία μόνιμου κλειδιού
    permanent_key = str(uuid.uuid4())
    expiration_date = timezone.now().date() + timezone.timedelta(days=30)  # Παράδειγμα για 30 μέρες

    license, created = License.objects.get_or_create(tenant=tenant)
    license.license_key = permanent_key
    license.hardware_id = hardware_id
    license.expiration_date = expiration_date
    license.active = True
    license.save()

    return JsonResponse({"permanent_key": permanent_key})

@csrf_exempt
def check_license(request):
    license_key = request.POST.get('license_key')
    hardware_id = request.POST.get('hardware_id')

    try:
        license = License.objects.get(license_key=license_key)
        if license.active and license.expiration_date > timezone.now().date():
            if license.hardware_id == hardware_id:
                return JsonResponse({"status": "valid"})
            else:
                return JsonResponse({"status": "invalid_hardware"})
        else:
            return JsonResponse({"status": "expired"})
    except License.DoesNotExist:
        return JsonResponse({"status": "no_license"})
