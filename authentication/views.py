from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
import os
import logging
import paypalrestsdk
from .forms import CustomUserCreationForm, PaymentForm, SubscriptionPlanForm, CustomUserLoginForm, TenantURLForm
from .models import Tenant, Domain, Subscription, CustomUser, License
from django.utils import timezone
from datetime import timedelta
import random
import string
import uuid
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
from decouple import config
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Ρύθμιση PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox ή live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

logger = logging.getLogger('django')

User = get_user_model()

@login_required
def paypal_payment(request):
    if request.method == "POST":
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('paypal_execute')),
                "cancel_url": request.build_absolute_uri(reverse('payment_cancelled'))},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "subscription",
                        "sku": "001",
                        "price": "10.00",
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": "10.00",
                    "currency": "USD"},
                "description": "Subscription payment."}]})

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    request.session['payment_id'] = payment.id
                    return redirect(approval_url)
        else:
            logger.error(payment.error)
            return render(request, 'payment/error.html', {'error': payment.error})
    return render(request, 'payment/paypal_payment.html')


@csrf_exempt
@login_required
def paypal_execute(request):
    payment_id = request.session.get('payment_id')
    payer_id = request.GET.get('PayerID')

    if not payment_id:
        return redirect('payment_error')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Ενημέρωση συνδρομής στη βάση δεδομένων
        subscription = Subscription.objects.filter(tenant__schema_name=request.user.username).first()
        if subscription:
            subscription.active = True
            subscription.save()

        # Αποστολή email στον πωλητή και τον αγοραστή
        send_mail(
            'Επιτυχής Πληρωμή',
            'Η πληρωμή σας ολοκληρώθηκε με επιτυχία.',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )

        # Δημιουργία προσωρινού κλειδιού
        temporary_key = generate_temporary_key()
        subscription.temporary_key = temporary_key
        subscription.save()

        return render(request, 'payment/success.html')
    else:
        return render(request, 'payment/error.html', {'error': payment.error})


@ensure_csrf_cookie
def get_csrf_token(request):
    logger.debug("Απόκτηση CSRF Token")
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})


@login_required
def payment_view(request):
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "10.00",
        "item_name": "Subscription",
        "invoice": "unique-invoice-id",  # Αναγνωριστικό συναλλαγής
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('payment_done')),
        "cancel_return": request.build_absolute_uri(reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "payment/payment.html", context)


def payment_done(request):
    return render(request, "payment/done.html")


def payment_cancelled(request):
    return render(request, "payment/canceled.html")


def payment_error(request):
    error_message = request.GET.get('error', 'Unknown error occurred.')
    context = {"error": error_message}
    return render(request, "payment/error.html", context)


def generate_temporary_key():
    return ''.join(random.choices(string.digits, k=8))

# Άλλες συναρτήσεις που χρησιμοποιούνται για διαχείριση χρηστών και συνδρομών
def create_user(username, password):
    if User.objects.filter(username=username).exists():
        return None, 'Το όνομα χρήστη υπάρχει ήδη.'

    user = User.objects.create_user(username=username, password=password)
    return user, None


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

            if plan == 'trial':
                end_date = timezone.now() + timedelta(days=30)
                price = 0
            else:
                end_date = timezone.now() + timedelta(days=365)
                price = 100

            Subscription.objects.create(
                tenant=tenant,
                subscription_type=plan,
                start_date=timezone.now(),
                end_date=end_date,
                price=price
            )

            login(request, user)
            messages.success(request, 'Ο λογαριασμός δημιουργήθηκε επιτυχώς! Παρακαλώ ολοκληρώστε την πληρωμή σας.')
            return redirect('payment_view')
        else:
            messages.error(request, 'Σφάλμα κατά την εγγραφή. Παρακαλώ ελέγξτε το φόρμα.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form})



@login_required
def profile_view(request):
    current_user = request.user
    tenant = None
    subscription = None
    temporary_key = None
    hardware_id = None
    computer_name = None

    try:
        tenant = Tenant.objects.get(schema_name=current_user.username)
        subscription = Subscription.objects.get(tenant=tenant)
        license = License.objects.get(tenant=tenant)
        hardware_id = license.hardware_id
        computer_name = license.computer_name

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
    except License.DoesNotExist:
        pass

    context = {
        'current_user': current_user,
        'tenant': tenant,
        'subscription': subscription,
        'temporary_key': temporary_key,
        'hardware_id': hardware_id,
        'computer_name': computer_name,
    }

    return render(request, 'authentication/profile.html', context)


@csrf_exempt
def activate_license(request):
    temporary_key = request.POST.get('temporary_key')
    hardware_id = request.POST.get('hardware_id')
    computer_name = request.POST.get('computer_name')

    try:
        subscription = Subscription.objects.get(temporary_key=temporary_key)
        tenant = subscription.tenant

        permanent_key = str(uuid.uuid4())
        expiration_date = timezone.now().date() + timezone.timedelta(days=30)

        license, created = License.objects.get_or_create(tenant=tenant)
        license.license_key = permanent_key
        license.hardware_id = hardware_id
        license.computer_name = computer_name
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

    return render(request, 'authentication/login.html', {'form': form})


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



@login_required
def select_subscription(request):
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data['plan']
            tenant = Tenant.objects.get(schema_name=request.user.username)
            subscription = Subscription.objects.get(tenant=tenant)
            if subscription:
                subscription.subscription_type = plan
                subscription.save()
                messages.success(request, 'Η συνδρομή σας ενημερώθηκε επιτυχώς!')
            else:
                # Δημιουργία νέας συνδρομής
                end_date = timezone.now() + timedelta(days=30) if plan == 'trial' else timezone.now() + timedelta(days=365)
                price = 0 if plan == 'trial' else 100
                Subscription.objects.create(
                    tenant=tenant,
                    subscription_type=plan,
                    start_date=timezone.now(),
                    end_date=end_date,
                    price=price
                )
                messages.success(request, 'Η νέα συνδρομή σας δημιουργήθηκε επιτυχώς!')
            return redirect('profile')
        else:
            messages.error(request, 'Σφάλμα κατά την επιλογή συνδρομής. Παρακαλώ ελέγξτε το φόρμα.')
    else:
        form = SubscriptionPlanForm()

    return render(request, 'authentication/select_subscription.html', {'form': form})






@login_required
def process_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            stripe_token = form.cleaned_data['stripeToken']

            try:
                charge = stripe.Charge.create(
                    amount=5000,
                    currency='usd',
                    description='Example charge',
                    source=stripe_token,
                )

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
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        customer_id = payment_intent['customer']

        temporary_key = str(uuid.uuid4())[:8]

    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']
        print('PaymentMethod was attached to a Customer!')

    else:
        print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)
