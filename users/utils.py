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


def create_otp(user, purpose, expiry_minutes=10):
    print("call create otp")
    # Delete any existing OTPs for this user and purpose
    OTP.objects.filter(user=user, purpose=purpose).delete()

    # Create new OTP
    otp = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

    otp_obj = OTP.objects.create(
        user=user,
        otp=otp,
        purpose=purpose,
        expires_at=expires_at
    )
    print(f"Generated OTP for {user.email}: {otp}")

    return otp_obj


def verify_otp(user, otp_code, purpose):
    print("call verify otp")
    try:
        otp_obj = OTP.objects.get(user=user, purpose=purpose, otp=otp_code)
        print(f"Verified OTP for {user.email}: {otp_code}")
        if otp_obj.is_valid():
            otp_obj.delete()  # OTP can only be used once
            return True
        return False
    except OTP.DoesNotExist:
        return False
    
