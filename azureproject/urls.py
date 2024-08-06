# azureproject/urls.py

from django.contrib import admin
from django.urls import include, path
from authentication.views import index  # Εισαγωγή του view για την αρχική σελίδα

urlpatterns = [
    path('', index, name='index'),  # Ανακατεύθυνση στην αρχική σελίδα
    path('tables/', include('tables.urls')),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('authentication/payment', include('authentication.urls')),  # Αυτή η γραμμή είναι προαιρετική αν καλύπτεται από την παραπάνω
    path('get-csrf-token/', include('authentication.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),  # Για το django-paypal αν το χρησιμοποιείτε
    path('accounts/', include('django.contrib.auth.urls')),  # Προσθήκη των URLs για τη διαχείριση των χρηστών
]
