from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User, EmailVerification
from users.utils import send_otp_email, create_otp
from django.utils import timezone
from datetime import timedelta
import uuid


@receiver(post_save, sender=User)
def create_email_verification(sender, instance, created, **kwargs):
    if created and not instance.is_email_verified:
        token = uuid.uuid4()
        expires_at = timezone.now() + timedelta(days=1)
        EmailVerification.objects.create(
            user=instance,
            token=token,
            expires_at=expires_at
        )
        otp = create_otp(instance, 'email_verification')
        send_otp_email(instance, otp, 'email_verification')