from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Subscription

class CustomUserCreationForm(UserCreationForm):
    PLAN_CHOICES = [
        ('trial', 'One Month Trial'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    plan = forms.ChoiceField(choices=PLAN_CHOICES, label='Επιλογή Συνδρομής')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'plan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['plan'].widget.attrs.update({'class': 'form-select'})

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

class SubscriptionPlanForm(forms.Form):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    plan = forms.ChoiceField(choices=PLAN_CHOICES, label='Επιλογή Προγράμματος')

class PaymentForm(forms.Form):
    stripeToken = forms.CharField(widget=forms.HiddenInput())

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['tenant', 'start_date', 'end_date', 'subscription_type', 'price']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
