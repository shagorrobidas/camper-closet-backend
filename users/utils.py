import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from django.conf import settings
from users.models import OTP
import secrets


def generate_reset_token(user_id):
    return secrets.token_urlsafe(32)


def generate_otp():
    return str(random.randint(1000, 9999))