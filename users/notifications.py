from users.models import Notification, NotificationSetting


def create_notification(
    user, title, body, notification_type='system',
    reference_id=None, reference_type=None
):
    """
    Utility function to create a notification for a user.
    Checks user notification settings before creation.
    """
    try:
        setting, _ = NotificationSetting.objects.get_or_create(user=user)
        if not setting.enabled:
            return None

        return Notification.objects.create(
            user=user,
            title=title,
            body=body,
            type=notification_type,
            reference_id=str(reference_id) if reference_id else None,
            reference_type=reference_type
        )
    except Exception as e:
        # Log error or handle gracefully
        print(f"Error creating notification: {e}")
        return None
