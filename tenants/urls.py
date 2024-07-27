
# tenants/urls.py
from django.urls import path

from . import views  # Εισαγωγή του αρχείου views


urlpatterns = [
    # path('register/', register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    # Προσθέστε εδώ τυχόν άλλα URLs
]
