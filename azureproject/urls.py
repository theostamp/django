# azureproject/urls.py
from django.contrib import admin
from django.urls import include, path
from authentication.views import get_csrf_token

urlpatterns = [
    path('tables/', include('tables.urls')),
    path('', include('tables.urls')),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('tenants/', include('tenants.urls')),
]
