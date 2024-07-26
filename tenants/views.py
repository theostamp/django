from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Tenant  # Υποθέτοντας ότι το μοντέλο του tenant είναι Tenant
from django.shortcuts import render, redirect
from .forms import SubscriptionForm


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



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Δημιουργία του χρήστη
            user = form.save()
            
            # Δημιουργία του tenant
            tenant = Tenant(name=form.cleaned_data['username'], owner=user)
            # Προσθέστε εδώ άλλες ρυθμίσεις για τον tenant αν χρειάζεται
            tenant.save()

            # Ανακατεύθυνση σε μια σελίδα επιτυχίας μετά την εγγραφή
            return redirect('success_url')  # Αντικαταστήστε με την επιθυμητή διεύθυνση

    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})
