"""azureproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path 
from tables import views as tables_views  
from authentication.views import register, get_csrf_token


urlpatterns = [
 

   

    path('tables/', include('tables.urls')), 
    path('', include('tables.urls')),  
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    # path('', views.index, name='index'),
    # path('', include('main.urls')),  # Κεντρική διαδρομή για την εφαρμογή main
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'), 
]
