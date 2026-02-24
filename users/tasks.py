from users.utils import send_otp_email, send_verification_email
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.template.exceptions import TemplateDoesNotExist
from users.models import User
from core.utils.exceptions import custom_exception_handler
import logging

logger = logging.getLogger('user')


def send_otp_email_task(user_id, otp, purpose):
    """
    Synchronously send an OTP email.
    """
    try:
        user = User.objects.get(id=user_id)
        send_otp_email(user, otp, purpose)
        print(f"Sent OTP email to {user.email} for {purpose} with OTP: {otp}")
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found for OTP email.")
        custom_exception_handler(f"User with id {user_id} not found for OTP email.")
    except Exception as e:
        logger.error(f"Error sending OTP email: {str(e)}")
        custom_exception_handler(e)


def send_verification_email_task(user_id, verification_url):
    """
    Synchronously send a verification email.
    """
    try:
        user = User.objects.get(id=user_id)
        send_verification_email(user, verification_url)
    except User.DoesNotExist as e:
        logger.error(f"User with id {user_id} not found for verification email.")
        custom_exception_handler(e)
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        custom_exception_handler(e)