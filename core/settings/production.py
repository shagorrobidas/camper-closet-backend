import os
from dotenv import load_dotenv
from .base import *

# Load production environment variables
if os.path.exists(BASE_DIR / '.env.production'):
    load_dotenv(BASE_DIR / '.env.production')

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database configuration (Postgres for production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Production security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Consider adding more security settings like:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
