# azureproject/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('tables/', include('tables.urls')),
    path('', include('tables.urls')),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('get-csrf-token/', include('authentication.urls')),  
    path('get-csrf-token/register/', include('authentication.urls')),  
    path('get-csrf-token/payment/', include('authentication.urls')),  
    # path('tenants/', include('tenants.urls')),
]
