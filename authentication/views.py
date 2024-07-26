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

            user, user_error = create_user(username, password)
            if user_error:
                messages.error(request, user_error)
                return render(request, 'authentication/register.html', {'form': form})

            login(request, user)
            messages.success(request, 'Ο λογαριασμός δημιουργήθηκε επιτυχώς!')
            return redirect('select_subscription')
        else:
            messages.error(request, 'Σφάλμα κατά την εγγραφή. Παρακαλώ ελέγξτε το φόρμα.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form})

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
