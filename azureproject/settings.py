import os
from pathlib import Path
from decouple import config  # Προσθήκη της σωστής εισαγωγής


BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# URL to use when referring to media files
MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Βεβαιωθείτε ότι αυτή η γραμμή δείχνει στον σωστό φάκελο
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


# Additional locations the staticfiles app will traverse if the FileSystemFinder finder is enabled.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# URL to use when referring to media files
MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


LOGIN_REDIRECT_URL = '/authentication/profile/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/authentication/login/'


SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '*', '[::1]', 'dign-fkh0cyakasa6cqf4.eastus-01.azurewebsites.net']

SHARED_APPS = [
    'django_tenants',
    'paypal.standard.ipn',
    'odoo_connect',
    'django.contrib.staticfiles',
    'authentication.apps.AuthenticationConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'corsheaders',
    'rest_framework',
]

TENANT_APPS = [
    'tables.apps.TablesConfig',
    'authentication.apps.AuthenticationConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'odoo_connect',
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



STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')



SESSION_ENGINE = "django.contrib.sessions.backends.cache"
ROOT_URLCONF = 'azureproject.urls'

TENANT_MODEL = "authentication.Tenant"
TENANT_DOMAIN_MODEL = "authentication.Domain"

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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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

CSRF_TRUSTED_ORIGINS = ['http://localhost:8003','http://127.0.0.1:8003']

from decouple import config

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')



CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY')

PAYPAL_MODE = 'sandbox'  # live για παραγωγή
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET')

# settings.py
PAYPAL_RECEIVER_EMAIL = 'theostam1966@gmail.com'
PAYPAL_TEST = True  # Ορίστε το σε False για την παραγωγή
# PAYPAL_ACCESS_TOKEN = 'access_token6V7rbVwmlM1gFZKW_8QtzWXqpcwQ6T5vhEGYNJDAAdn3paCgRpdeMdVYmWzgbKSsECednupJ3Zx5Xd-g'
PAYPAL_ACCESS_TOKEN = None
PAYPAL_API_BASE_URL = 'https://api-m.sandbox.paypal.com'

# settings.py στο Django


# ΜΟΝΟ ΚΑΤΑ ΤΗ ΦΑΣΗ ΑΝΑΠΤΥΞΗΣ
# SESSION SETTINGS

# Απενεργοποίηση της ασφάλειας για το cookie του session (Secure flag) ώστε να επιτρέπεται η χρήση σε μη ασφαλείς (HTTP) συνδέσεις
SESSION_COOKIE_SECURE = False

# Ενεργοποίηση του HTTPOnly flag για προστασία του session από προσβάσεις μέσω JavaScript
SESSION_COOKIE_HTTPONLY = True

# Απενεργοποίηση του SameSite flag για τα session cookies για να μην αποτρέπεται η αποστολή τους σε διαφορετικό domain
SESSION_COOKIE_SAMESITE = None  # Ή 'Lax' για περιορισμένη ασφάλεια

# Ορίστε το SESSION_ENGINE για να χρησιμοποιήσετε cookies για session (προεπιλογή)
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# Αν χρησιμοποιείτε τη βάση δεδομένων για τα sessions
# SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Ρύθμιση διάρκειας ζωής του session (σε δευτερόλεπτα). Αν είναι 0, το session λήγει μόλις κλείσει το browser.
SESSION_COOKIE_AGE = 1209600  # 2 εβδομάδες

# Προαιρετικά: Απενεργοποίηση αποστολής του session cookie σε κάθε αίτηση (για βελτίωση απόδοσης)
SESSION_SAVE_EVERY_REQUEST = False

# Χειρισμός της διάρκειας ζωής του session όταν ο χρήστης κλείσει τον browser
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSP_DEFAULT_SRC = ("'self'",)
# # CSP_STYLE_SRC = ("'self'", "https://www.paypal.com", "'unsafe-inline'")
# CSP_SCRIPT_SRC = ("'self'", "https://www.paypal.com", "https://www.paypalobjects.com")

