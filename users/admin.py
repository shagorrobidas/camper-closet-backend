from django.contrib import admin
from users.models import User, OTP, EmailVerification, Notification, NotificationSetting


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
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


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'otp', 'purpose', 'created_at', 'expires_at')
    list_filter = ('purpose',)
    search_fields = ('user__email', 'otp')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'type', 'title', 'is_read', 'created_at'
    )
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'body')
    ordering = ('-created_at',)


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'enabled', 'packing_reminders',
        'milestone_achievements', 'weekly_summaries'
    )
    list_filter = (
        'enabled', 'packing_reminders',
        'milestone_achievements', 'weekly_summaries'
    )
    search_fields = ('user__email',)
