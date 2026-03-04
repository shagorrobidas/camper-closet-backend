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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# In development, it's often easier to serve static files from the project root.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
