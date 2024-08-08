from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'subscription_type', 'start_date', 'end_date', 'active')
    search_fields = ('tenant__name', 'temporary_key')
    list_filter = ('subscription_type', 'active', 'start_date', 'end_date')
    ordering = ('tenant',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Εδώ ορίζουμε τις ετικέτες για τα πεδία στη φόρμα του admin
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        # Εδώ μπορείτε να προσθέσετε πρόσθετα πεδία που έχετε στο μοντέλο CustomUser
        # Για παράδειγμα: (_('Additional Info'), {'fields': ('your_custom_field',)})
    )
    # Αυτό ορίζει τα πεδία που θα εμφανίζονται στη λίστα των χρηστών στο admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    # Ορίστε πεδία μέσω των οποίων μπορείτε να φιλτράρετε τους χρήστες στο admin
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    # Ορίστε τα πεδία αναζήτησης για να βρίσκετε χρήστες με βάση συγκεκριμένα στοιχεία
    search_fields = ('username', 'first_name', 'last_name', 'email')
    # Ορίστε τη σειρά με την οποία θα ταξινομούνται οι χρήστες στη λίστα
    ordering = ('username',)

from django.contrib import admin
from .models import Tenant, Domain

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'created_on')
    search_fields = ('name', 'schema_name')
    list_filter = ('created_on',)
    ordering = ('name',)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant')
    search_fields = ('domain', 'tenant__name')  # Η διπλή υπογράμμιση χρησιμοποιείται για την πρόσβαση σε σχετικά πεδία
    list_filter = ('tenant__name',)
    ordering = ('domain',)
