

# tenants/urls.py

from django.urls import path
from tenants import views
from tenants.authentication import views as auth_views

urlpatterns = [
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.login_view, name='login'),
    path('profile/', auth_views.profile_view, name='profile'),
    path('payment/', auth_views.process_payment, name='payment'),
    path('select_subscription/', auth_views.select_subscription, name='select_subscription'),
    path('features/', auth_views.features, name='features'),
    path('integrations/', auth_views.integrations, name='integrations'),
    path('pricing/', auth_views.pricing, name='pricing'),
    path('contacts/', auth_views.contacts, name='contacts'),
    path('index/', auth_views.index, name='index'),
    path('setup_url/', auth_views.setup_url, name='setup_url'),
    path('stripe_webhook/', auth_views.stripe_webhook, name='stripe_webhook'),
    path('payment_view/', auth_views.payment_view, name='payment_view'),
    path('password_change/', auth_views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('generate_temporary_key/', views.generate_temporary_key, name='generate_temporary_key'),
    path('activate_license/', views.activate_license, name='activate_license'),
    path('check_license/', views.check_license, name='check_license'),
    path('payment/start/', views.start_payment, name='start_payment'),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('get-csrf-token/', auth_views.get_csrf_token, name='get_csrf_token'),  # Βεβαιωθείτε ότι αυτή η διαδρομή υπάρχει
]
