# azureproject/urls.py

from django.contrib import admin
from django.urls import include, path
from authentication.views import index, payment_error

urlpatterns = [
    path('', index, name='index'),
    path('tables/', include('tables.urls')),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('get-csrf-token/', include('authentication.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('error/', payment_error, name='error'),  # Προσθήκη του URL pattern για το error
]
