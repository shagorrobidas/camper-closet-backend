import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from users.models import OTP
import secrets


def generate_reset_token(user_id):
    return secrets.token_urlsafe(32)


def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp_email(user, otp, purpose):
    print(f"call send otp email {user} otp {otp} purpose {purpose}")
    subject = f"Your OTP for {purpose.replace('_', ' ').title()}"

    context = {
        'user': user,
        'otp': otp,
        'purpose': purpose,
    }

    # Make sure that when purpose is "change_email", we send to the new email
    if purpose == "change_email":
        print(f"Sending OTP email to {user.new_email} for {purpose} with OTP: {otp}")  
        message = render_to_string('emails/email_change_email.html', context)
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.new_email]  # Use the new email field here
        )
    else:
        print(f"Sending OTP email to {user.email} for {purpose} with OTP: {otp}")  # For other purposes
        message = render_to_string('emails/otp_email.html', context)
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )

    email.content_subtype = 'html'
    email.send()
