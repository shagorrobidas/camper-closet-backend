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


def send_welcome_email(user_id):
    """
    Synchronously send a welcome email.
    """
    try:
        user = User.objects.get(id=user_id)

        html_message = render_to_string(
            'emails/welcome_email.html', {'user': user}
        )
        # fallback for clients that can't render HTML (optional)
        # plain_message = strip_tags(html_message)

        subject = 'Welcome to Comper Closet App!'

        msg = EmailMessage(
            subject,
            html_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)

        print(f"Sent welcome email to {user.email}")
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist for welcome email.")
        custom_exception_handler(f"User with id {user_id} does not exist for welcome email.")
    except TemplateDoesNotExist as e:
        logger.error(f"Email template not found: {str(e)}")
        custom_exception_handler(e)
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
        custom_exception_handler(e)