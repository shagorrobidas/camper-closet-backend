import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from django.contrib.auth import authenticate
from users.models import User

user = User.objects.first()
if user:
    print(f"First user: {user.email}")
    user.set_password("password123")
    user.is_email_verified = True
    user.save()
    auth_user = authenticate(email=user.email, password="password123")
    print(f"Auth user (email kwarg): {auth_user}")
    auth_user2 = authenticate(username=user.email, password="password123")
    print(f"Auth user (username kwarg): {auth_user2}")
else:
    print("No users found.")
