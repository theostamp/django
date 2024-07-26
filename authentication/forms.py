from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
from tenants.models import Tenant, Domain

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class CustomUserLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class TenantURLForm(forms.Form):
    tenant_url = forms.CharField(label='Διεύθυνση URL του Tenant', max_length=100)
