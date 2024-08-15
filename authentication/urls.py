# authentication/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('setup_url/', views.setup_url, name='setup_url'),
    path('user-credits/', views.user_credits, name='user_credits'),
    path('select_subscription/', views.select_subscription, name='select_subscription'),
    path('login/', views.login_view, name='login'),
    path('features/', views.features, name='features'),
    path('integrations/', views.integrations, name='integrations'),
    path('pricing/', views.pricing, name='pricing'),
    path('contacts/', views.contacts, name='contacts'),
    path('password_reset/', include('django.contrib.auth.urls')),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('payment/', views.payment_view, name='payment_view'),
    path('profile/', views.profile_view, name='profile'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change_done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
    # path('generate_temporary_key/', views.generate_temporary_key, name='generate_temporary_key'),
    path('activate_license/', views.activate_license, name='activate_license'),
    path('check_license/', views.check_license, name='check_license'),
    path('paypal/', views.paypal_payment, name='paypal_payment'),
    path('paypal/execute/', views.paypal_execute, name='paypal_execute'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('payment/done/', views.payment_done, name='payment_done'),
    path('payment/error/', views.payment_error, name='payment_error'),
    path('paypal-ipn/', include('paypal.standard.ipn.urls')),
    path('create-subscription/', views.create_subscription, name='create_subscription'),
    path('change-subscription/', views.change_subscription, name='change_subscription'),
    path('api/register-device/', views.register_device, name='register_device'),
    path('api/authenticate-device/', views.authenticate_device, name='authenticate_device'),
    path('register-mac-address/<str:username>/', views.register_mac_address, name='register_mac_address'),

]
