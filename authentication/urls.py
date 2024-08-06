# authentication/urls.py
from django.urls import path
from . import views
from django.urls import include, path


urlpatterns = [
    path('signup/', views.register, name='register'),
    path('setup_url/', views.setup_url, name='setup_url'),
    path('user-credits/', views.user_credits, name='user_credits'),
    path('select_subscription/', views.select_subscription, name='select_subscription'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('features/', views.features, name='features'),
    path('integrations/', views.integrations, name='integrations'),
    path('pricing/', views.pricing, name='pricing'),
    path('contacts/', views.contacts, name='contacts'),
    path('password_reset/', include('django.contrib.auth.urls')),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('payment/', views.process_payment, name='payment'),
    path('profile/', views.profile_view, name='profile'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change_done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('generate_temporary_key/', views.generate_temporary_key, name='generate_temporary_key'),
    path('activate_license/', views.activate_license, name='activate_license'),
    path('check_license/', views.check_license, name='check_license'),
    path('payment/create/', views.create_payment, name='create_payment'),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('payment/cancel/', views.payment_cancelled, name='payment_cancelled'),
    path('payment/error/', views.payment_error, name='error'),  # Προσθήκη του URL pattern για το error
    path('paypal-payment/', views.paypal_payment, name='paypal_payment'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
]
