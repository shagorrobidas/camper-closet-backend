from django.contrib import admin
from unfold.admin import ModelAdmin
from users.models import User, OTP, EmailVerification, Notification, NotificationSetting


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        'pk', 'email', 'role', 'full_name',
        'is_email_verified',
        'is_active', 'is_superuser'
    )
    list_filter = (
        'email', 'full_name',
        'is_email_verified',
        'is_active', 'is_staff', 'is_superuser'
    )
    search_fields = ('email', 'full_name')
    ordering = ('id',)


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = (
        'id', 'user', 'type', 'title', 'is_read', 'created_at'
    )
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'body')
    ordering = ('-created_at',)


@admin.register(NotificationSetting)
class NotificationSettingAdmin(ModelAdmin):
    list_display = (
        'id', 'user', 'enabled', 'packing_reminders',
        'milestone_achievements', 'weekly_summaries'
    )
    list_filter = (
        'enabled', 'packing_reminders',
        'milestone_achievements', 'weekly_summaries'
    )
    search_fields = ('user__email',)
