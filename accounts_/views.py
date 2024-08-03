# tenants/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Tenant, Subscription, License, Order, TemporaryKey
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import paypalrestsdk
import uuid
import random
import string
from django.conf import settings

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

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
