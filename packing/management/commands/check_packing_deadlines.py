from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from packing.models import Trip
from users.notifications import create_notification


class Command(BaseCommand):
    help = (
        'Check for trips whose packing deadline passed 1 day ago '
        'and send notifications.'
    )

    def handle(self, *args, **options):

        target_date = (timezone.now() - timedelta(days=1)).date()

        # Filter for active trips where the packing deadline matches
        # the target date
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

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully sent {count} packing deadline notifications.'
            )
        )
