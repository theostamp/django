from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()

def create_user(username, password):
    try:
        user = User.objects.create_user(username=username, password=password)
        return user, None
    except Exception as e:
        return None, str(e)

def create_tenant(user, plan):
    try:
        tenant = Tenant.objects.create(user=user, subscription_type=plan)
        return tenant, None
    except Exception as e:
        return None, str(e)
