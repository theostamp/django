import os
from django.core.exceptions import ImproperlyConfigured
from .settings import *  # noqa
from .settings import BASE_DIR
from django.db import connection
from django_tenants.utils import schema_context


# Ρυθμίστε το σχήμα στη δημόσια βάση δεδομένων κατά την εκκίνηση
try:
    connection.set_schema_to_public()
except Exception as e:
    print(f"Unexpected error setting schema to public on startup: {e}")

# Configure the domain name using the environment variable that Azure automatically creates for us.
# ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
# CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
DEBUG = True


ALLOWED_HOSTS = [
    'dign-fkh0cyakasa6cqf4.eastus-01.azurewebsites.net',
    'digns.net',
    'theo.digns.net',
    'demo.digns.net',
    '*',
]

CSRF_TRUSTED_ORIGINS = [
    'https://dign-fkh0cyakasa6cqf4.eastus-01.azurewebsites.net',
    'https://digns.net',
    'https://theo.digns.net',
    'https://demo.digns.net',
]

CORS_ALLOWED_ORIGINS = [
    'http://dign-fkh0cyakasa6cqf4.eastus-01.azurewebsites.net',
    'https://dign-fkh0cyakasa6cqf4.eastus-01.azurewebsites.net',
    'https://digns.net',
    'https://theo.digns.net',
]


# WhiteNoise configuration
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # Add whitenoise middleware after the security middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')




# Configure Postgres database based on connection string of the libpq Keyword/Value form
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': conn_str_params['dbname'],
        'HOST': conn_str_params['host'],
        'USER': conn_str_params['user'],
        'PASSWORD': conn_str_params['password'],
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)


# CACHES = {
#     "default": {  
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": os.environ.get('AZURE_REDIS_CONNECTIONSTRING'),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#         },
#     }
# }




TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"
TENANTS_BASE_FOLDER = os.path.join(BASE_DIR, 'tenants_folders')