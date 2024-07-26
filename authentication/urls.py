from django.urls import path
from . import views

urlpatterns = [
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('setup_url/', views.setup_url, name='setup_url'),
    path('user-credits/', views.user_credits, name='user_credits'),
]
