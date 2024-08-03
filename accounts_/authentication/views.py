from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
import stripe
import os
import logging
import uuid
import random
import string
import paypalrestsdk

from .forms import CustomUserCreationForm, CustomUserLoginForm, TenantURLForm, SubscriptionPlanForm, PaymentForm
from tenants.models import Tenant, Domain, Subscription, TemporaryKey, CustomUser, License, Order

# Προσθήκη των εισαγωγών για αλλαγή κωδικού πρόσβασης
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

# Ρύθμιση Stripe API
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
logger = logging.getLogger('django')
User = get_user_model()

# Ρύθμιση PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # Χρησιμοποιήστε "live" για παραγωγικό περιβάλλον
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def generate_temporary_key():
    return ''.join(random.choices(string.digits, k=8))

@ensure_csrf_cookie
def get_csrf_token(request):
    logger.debug("Απόκτηση CSRF Token")
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})

@csrf_exempt
def activate_license(request):
    temporary_key = request.POST.get('temporary_key')
    hardware_id = request.POST.get('hardware_id')
    computer_name = request.POST.get('computer_name')

    try:
        temporary_key_obj = TemporaryKey.objects.get(key=temporary_key, expires_at__gt=timezone.now())
        tenant = temporary_key_obj.tenant

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
    except TemporaryKey.DoesNotExist:
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

def create_tenant(user, plan):
    with schema_context('public'):
        if Tenant.objects.filter(schema_name=user.username).exists():
            return None, "Το σχήμα αυτό υπάρχει ήδη."

        try:
            tenant = Tenant(schema_name=user.username, name=user.username, subscription_type=plan)
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

            tenant, tenant_error = create_tenant(user, plan)
            if tenant_error:
                messages.error(request, tenant_error)
                return render(request, 'authentication/register.html', {'form': form})

            # Δημιουργία συνδρομής με βάση την επιλογή του χρήστη
            if plan == 'trial':
                end_date = timezone.now() + timedelta(days=30)
                price = 0
            else:
                end_date = timezone.now() + timedelta(days=365)  # Παράδειγμα για ετήσια συνδρομή
                price = 100  # Τιμή για την ετήσια συνδρομή (παράδειγμα)

            Subscription.objects.create(
                tenant=tenant,
                subscription_type=plan,
                start_date=timezone.now(),
                end_date=end_date,
                price=price
            )

            login(request, user)
            messages.success(request, 'Ο λογαριασμός δημιουργήθηκε επιτυχώς! Παρακαλώ ολοκληρώστε την πληρωμή σας.')
            return redirect('payment')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'authentication/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form})

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
                tenant = Tenant.objects.get(schema_name=request.user.username)
                subscription = Subscription.objects.get(tenant=tenant)
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
            tenant, tenant_error = create_tenant(request.user, form.cleaned_data['plan'])
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
                return redirect('profile')  # Ανακατεύθυνση στην προσωπική σελίδα του χρήστη
            else:
                logger.warning("Login failed: Invalid username or password")
                messages.error(request, 'Λάθος όνομα χρήστη ή κωδικός')
        else:
            logger.warning("Login failed: Invalid form data")
            messages.error(request, 'Μη έγκυρα στοιχεία φόρμας')
    else:
        form = CustomUserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request):
    current_user = request.user
    tenant = None
    subscription = None
    temporary_key = None

    try:
        tenant = Tenant.objects.get(schema_name=current_user.username)
        subscription = Subscription.objects.get(tenant=tenant)

        # Αναζήτηση για υπάρχον προσωρινό κλειδί που δεν έχει λήξει
        try:
            temporary_key_obj = TemporaryKey.objects.get(tenant=tenant, expires_at__gt=timezone.now())
            temporary_key = temporary_key_obj.key
        except TemporaryKey.DoesNotExist:
            temporary_key = generate_temporary_key()
            TemporaryKey.objects.create(tenant=tenant, customer_id=current_user.id, key=temporary_key)

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

    return render(request, 'authentication/profile.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'authentication/password_change.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'authentication/password_change_done.html'

def features(request):
    return render(request, 'authentication/features.html')

def integrations(request):
    return render(request, 'authentication/integrations.html')

def pricing(request):
    return render(request, 'authentication/pricing.html')

def contacts(request):
    return render(request, 'authentication/contacts.html')

def index(request):
    return render(request, 'authentication/index.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'your_webhook_secret'

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        customer_id = payment_intent['customer']

        # Generate temporary key
        temporary_key = str(uuid.uuid4())[:8]

        # Save the temporary key in the database, associated with the customer_id
        TemporaryKey.objects.create(customer_id=customer_id, key=temporary_key)

        print(f'Successful payment! Temporary key generated: {temporary_key}')
        # Send the temporary key to the user by email or other means

    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']
        print('PaymentMethod was attached to a Customer!')

    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)

@login_required
def payment_view(request):
    return render(request, 'payment/payment.html')

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

@login_required
def start_payment(request):
    if request.method == "POST":
        current_user = request.user
        tenant = get_object_or_404(Tenant, schema_name=current_user.username)

        order = Order.objects.create(
            tenant=tenant,
            amount=request.POST['amount'],
            currency='USD',
            status='Pending'
        )

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/payment/execute/'),
                "cancel_url": request.build_absolute_uri('/payment/cancel/')
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Order #{}".format(order.id),
                        "sku": "item",
                        "price": str(order.amount),
                        "currency": order.currency,
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(order.amount),
                    "currency": order.currency
                },
                "description": "Payment for Order #{}".format(order.id)
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    order.order_id = payment.id
                    order.save()
                    request.session['payment_id'] = payment.id
                    return redirect(approval_url)
        else:
            print(payment.error)

    return render(request, 'payment/start_payment.html')

@login_required
def execute_payment(request):
    payment_id = request.session.get('payment_id')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        return render(request, 'payment/payment_failed.html', {'error': 'Missing payment information.'})

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        order = get_object_or_404(Order, order_id=payment_id)
        order.status = 'Completed'
        order.save()
        del request.session['payment_id']
        return render(request, 'payment/payment_success.html', {'order': order})
    else:
        return render(request, 'payment/payment_failed.html', {'error': payment.error})

@login_required
def payment_cancel(request):
    return render(request, 'payment/payment_cancel.html')

@login_required
def payment_failed(request):
    return render(request, 'payment/payment_failed.html', {'error': 'Payment was not successful. Please try again.'})