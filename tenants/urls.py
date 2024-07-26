
# tenants/urls.py
from django.urls import path
from .views import register
from . import views  # Εισαγωγή του αρχείου views


urlpatterns = [
    path('register/', register, name='register'),
    path('accounts/profile/', views.profile_view, name='profile'),
    # Προσθέστε εδώ τυχόν άλλα URLs
]
