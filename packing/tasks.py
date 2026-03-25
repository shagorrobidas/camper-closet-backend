from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from packing.models import Trip
from users.notifications import create_notification


@shared_task
def check_packing_deadlines_task():
    target_date = (timezone.now() - timedelta(days=1)).date()

    trips = Trip.objects.filter(
        packing_deadline=target_date, status='Active'
    )

    count = 0
    for trip in trips:
        create_notification(
            user=trip.user,
            title="Packing Deadline Passed",
            body=(
                f"Your packing deadline for trip "
                f"'{trip.name}' passed yesterday."
            ),
            notification_type='system',
            reference_id=trip.id,
            reference_type='trip'
        )
        count += 1

    return f"Successfully sent {count} packing deadline notifications."
