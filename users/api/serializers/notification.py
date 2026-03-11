from rest_framework import serializers
from users.models import Notification, NotificationSetting


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'title',
            'body',
            'type',
            'reference_id',
            'reference_type',
            'is_read',
            'created_at',
        ]
        read_only_fields = [
            'id', 'user', 'title', 'body', 'type',
            'reference_id', 'reference_type', 'created_at'
        ]


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = [
            'id',
            'user',
            'enabled',
            'packing_reminders',
            'milestone_achievements',
            'weekly_summaries',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'updated_at']
