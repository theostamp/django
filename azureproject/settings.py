# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


import os

# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = '/static/'

# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional locations the staticfiles app will traverse if the FileSystemFinder finder is enabled.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# URL to use when referring to media files
MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

DEBUG = True

ALLOWED_HOSTS = ['localhost', 'localhost', '*','[::1]','dign-fkh0cyakasa6cqf4.eastus-01.azurewebsites.net']



SHARED_APPS = [
    'django_tenants',
    'tenants.apps.TenantsConfig',
    'authentication.apps.AuthenticationConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
]

TENANT_APPS = [
    'tables.apps.TablesConfig',
    # 'restaurant_review.apps.RestaurantReview.Config',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
ROOT_URLCONF = 'azureproject.urls'

TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.environ.get('DBNAME'),
        'HOST': os.environ.get('DBHOST'),
        'USER': os.environ.get('DBUSER'),
        'PASSWORD': os.environ.get('DBPASS'),
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

AUTH_USER_MODEL = 'authentication.CustomUser'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Προσθέστε το path στον φάκελο templates αν δεν είναι εκεί
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]




DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF_TRUSTED_ORIGINS = ['http://localhost:8081']
# CSRF_COOKIE_SECURE = False
# APPEND_SLASH = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'azureproject': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'tables.views': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

TENANTS_BASE_FOLDER = os.path.join(BASE_DIR, 'tenants_folders')
CSRF_TRUSTED_ORIGINS = ['http://localhost:8003']
