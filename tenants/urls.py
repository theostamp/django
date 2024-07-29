# tenants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('generate_temporary_key/', views.generate_temporary_key, name='generate_temporary_key'),
    path('activate_license/', views.activate_license, name='activate_license'),
    path('check_license/', views.check_license, name='check_license'),

]
