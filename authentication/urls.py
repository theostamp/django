# authentication/urls.py
from django.urls import path, include
from . import views

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
]
