
# tenants/views.py
from django.shortcuts import render, redirect
# from .forms import RegistrationForm
from .models import Tenant  # Υποθέτοντας ότι το μοντέλο του tenant είναι Tenant
from django.shortcuts import render, redirect
from .forms import SubscriptionForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tenants.models import Tenant, Subscription

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

def add_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('some-view')  # Αντικαταστήστε με το όνομα της επιθυμητής προορισμού σελίδας
    else:
        form = SubscriptionForm()

    return render(request, 'tenants/add_subscription.html', {'form': form})


