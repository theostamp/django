
# authentication/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomUserLoginForm, TenantURLForm, SubscriptionPlanForm
from django.contrib import messages
from django.db import IntegrityError
from tenants.models import Tenant, Domain
from .models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Subscription
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta
import stripe
from django.conf import settings
from .forms import CustomUserCreationForm, PaymentForm
from .models import CustomUser, Subscription
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger('django')

User = get_user_model()

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})

@login_required
def user_credits(request):
    current_user = request.user
    tenant_domains = []

    try:
        tenants = Tenant.objects.filter(schema_name=current_user.username)
        for tenant in tenants:
            domains = Domain.objects.filter(tenant=tenant)
            tenant_domains.extend(domains)
    except Tenant.DoesNotExist:
        pass

    context = {
        'current_user': current_user,
        'tenant_domains': tenant_domains,
    }
    return render(request, 'authentication/user_credits.html', context)

def create_tenant(user):
    with schema_context('public'):
        if Tenant.objects.filter(schema_name=user.username).exists():
            return None, "Το σχήμα αυτό υπάρχει ήδη."

        try:
            tenant = Tenant(schema_name=user.username, name=user.username)
            tenant.save()
            create_folders_for_tenant(user.username)
            domain_name = f"{user.username}.127.0.0.1:8003"
            Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)
        except IntegrityError:
            return None, "Προέκυψε σφάλμα κατά τη δημιουργία του tenant."

    with schema_context(tenant.schema_name):
        pass

    return tenant, None

def create_folders_for_tenant(tenant_name):
    base_tenant_folder = settings.TENANTS_BASE_FOLDER
    os.makedirs(base_tenant_folder, exist_ok=True)

    categories = ['received_orders', 'upload_json']
    for category in categories:
        tenant_folder = os.path.join(base_tenant_folder, f'{tenant_name}_{category}')
        os.makedirs(tenant_folder, exist_ok=True)

def setup_url(request):
    if request.method == 'POST':
        form = TenantURLForm(request.POST)
        if form.is_valid():
            tenant_url = form.cleaned_data['tenant_url']

            if Tenant.objects.filter(schema_name=tenant_url).exists():
                messages.error(request, "Το σχήμα αυτό υπάρχει ήδη.")
                return render(request, 'authentication/setup_url.html', {'form': form})

            try:
                with schema_context('public'):
                    new_tenant = Tenant(schema_name=tenant_url, name=tenant_url)
                    new_tenant.save()

                messages.success(request, "Ο νέος tenant δημιουργήθηκε επιτυχώς.")
                return redirect('user_credits')
            except IntegrityError:
                messages.error(request, "Προέκυψε σφάλμα κατά τη δημιουργία του tenant.")
                return render(request, 'authentication/setup_url.html', {'form': form})
    else:
        form = TenantURLForm()

    return render(request, 'authentication/setup_url.html', {'form': form})

def create_user(username, password):
    if User.objects.filter(username=username).exists():
        return None, 'Το όνομα χρήστη υπάρχει ήδη.'

    user = User.objects.create_user(username=username, password=password)
    return user, None



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            plan = form.cleaned_data.get('plan')

            user, user_error = create_user(username, password)
            if user_error:
                messages.error(request, user_error)
                return render(request, 'authentication/register.html', {'form': form})

            # Δημιουργία συνδρομής με βάση την επιλογή του χρήστη
            if plan == 'trial':
                end_date = timezone.now() + timedelta(days=30)
            else:
                end_date = timezone.now() + timedelta(days=365)  # Παράδειγμα για ετήσια συνδρομή

            # Δημιουργία της συνδρομής χωρίς να την ενεργοποιήσουμε ακόμα
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                start_date=timezone.now(),
                end_date=end_date,
                active=False
            )

            login(request, user)
            messages.success(request, 'Ο λογαριασμός δημιουργήθηκε επιτυχώς! Παρακαλώ ολοκληρώστε την πληρωμή σας.')
            return redirect('payment')
        else:
            messages.error(request, 'Σφάλμα κατά την εγγραφή. Παρακαλώ ελέγξτε το φόρμα.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form})

# authentication/views.py
@login_required
def process_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            stripe_token = form.cleaned_data['stripeToken']

            try:
                charge = stripe.Charge.create(
                    amount=5000,  # Το ποσό σε cents (π.χ. $50.00)
                    currency='usd',
                    description='Example charge',
                    source=stripe_token,
                )
                # Εύρεση της συνδρομής και ενεργοποίησή της
                subscription = Subscription.objects.get(user=request.user, active=False)
                subscription.active = True
                subscription.save()

                messages.success(request, 'Η πληρωμή σας ολοκληρώθηκε με επιτυχία!')
                return redirect('index')
            except stripe.error.CardError as e:
                messages.error(request, f'Η πληρωμή απέτυχε: {e.error.message}')
        else:
            messages.error(request, 'Παρακαλώ δοκιμάστε ξανά.')
    else:
        form = PaymentForm()

    return render(request, 'authentication/payment.html', {'form': form, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY})


@login_required
def select_subscription(request):
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            # Προσθήκη λογικής για την επιλογή συνδρομητικού προγράμματος
            tenant, tenant_error = create_tenant(request.user)
            if tenant_error:
                messages.error(request, tenant_error)
                return render(request, 'authentication/select_subscription.html', {'form': form})

            messages.success(request, 'Ο tenant δημιουργήθηκε επιτυχώς!')
            return redirect('user_credits')
        else:
            messages.error(request, 'Σφάλμα κατά την επιλογή συνδρομής. Παρακαλώ ελέγξτε το φόρμα.')
    else:
        form = SubscriptionPlanForm()

    return render(request, 'authentication/select_subscription.html', {'form': form})

def login_view(request):
    logger.debug(f"Request method: {request.method}")
    if request.method == 'POST':
        logger.debug(f"Login form data: {request.POST}")
        form = CustomUserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                logger.debug("Login successful")
                return JsonResponse({'success': True, 'message': 'Επιτυχής σύνδεση'})
            else:
                logger.warning("Login failed: Invalid username or password")
                return JsonResponse({'success': False, 'message': 'Λάθος όνομα χρήστη ή κωδικός'}, status=401)
        else:
            logger.warning("Login failed: Invalid form data")
            return JsonResponse({'success': False, 'message': 'Μη έγκυρα στοιχεία φόρμας'}, status=400)
    else:
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            logger.error("Login failed: Invalid request method")
            return JsonResponse({'success': False, 'message': 'Μη επιτρεπτό αίτημα'}, status=400)
        else:
            messages.error(request, 'Παρακαλώ χρησιμοποιήστε την εφαρμογή για να συνδεθείτε.')
            return render(request, 'authentication/login.html')

def features(request):
    return render(request, 'authentication/features.html')

def integrations(request):
    return render(request, 'authentication/integrations.html')

def pricing(request):
    return render(request, 'authentication/pricing.html')

def contacts(request):
    return render(request, 'authentication/contacts.html')

def index(request):
    return render(request, 'authentication/ ')



