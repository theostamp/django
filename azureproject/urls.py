# azureproject/urls.py
# urls.py
from django.contrib import admin
from django.urls import include, path
from authentication.views import index  # Εισαγωγή του view για την αρχική σελίδα

urlpatterns = [
    path('', index, name='index'),  # Προσθήκη του URL pattern για την αρχική σελίδα
    path('tables/', include('tables.urls')),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('get-csrf-token/', include('authentication.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),  # Προσθήκη των URL patterns για το PayPal
]
