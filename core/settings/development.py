import os
from dotenv import load_dotenv
from .base import *

# Load development environment variables
if os.path.exists(BASE_DIR / '.env.development'):
    load_dotenv(BASE_DIR / '.env.development')
else:
    load_dotenv(BASE_DIR / '.env')

DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

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

# In development, it's often easier to serve static files from the project root.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
