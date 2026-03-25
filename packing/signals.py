from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Trip
from users.notifications import create_notification


@receiver(post_save, sender=Trip)
def create_trip_notification(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a new trip is created.
    """
    if created:
        create_notification(
            user=instance.user,
            title="New Trip Created",
            body=f"Your trip '{instance.name}' has been created successfully.",
            notification_type='system',
            reference_id=instance.id,
            reference_type='trip'
        )
