
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
import random
import string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Tenant, Subscription, License
from django.utils import timezone
import uuid

def generate_temporary_key():
    return ''.join(random.choices(string.digits, k=8))

@login_required
def profile_view(request):
    current_user = request.user
    tenant = None
    subscription = None
    temporary_key = None

    try:
        tenant = Tenant.objects.get(schema_name=current_user.username)
        subscription = Subscription.objects.get(tenant=tenant)
        # Αν δεν υπάρχει προσωρινό κλειδί, δημιουργήστε ένα νέο
        if not subscription.temporary_key:
            temporary_key = generate_temporary_key()
            subscription.temporary_key = temporary_key
            subscription.save()
        else:
            temporary_key = subscription.temporary_key
    except Tenant.DoesNotExist:
        pass
    except Subscription.DoesNotExist:
        pass

    context = {
        'current_user': current_user,
        'tenant': tenant,
        'subscription': subscription,
        'temporary_key': temporary_key,
    }

    return render(request, 'tenants/profile.html', context)

@csrf_exempt
def activate_license(request):
    temporary_key = request.POST.get('temporary_key')
    hardware_id = request.POST.get('hardware_id')
    computer_name = request.POST.get('computer_name')

    try:
        # Βρείτε την συνδρομή με το προσωρινό κλειδί
        subscription = Subscription.objects.get(temporary_key=temporary_key)
        tenant = subscription.tenant

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
    except Subscription.DoesNotExist:
        return JsonResponse({"status": "invalid_temporary_key"}, status=400)

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
