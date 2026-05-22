from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from users.models import (
    User,
    OTP,
    EmailVerification,
    Notification,
    NotificationSetting,
    UserSubscriptionHistory
)
from packing.models import Trip


class TripInline(TabularInline):
    model = Trip
    extra = 0
    show_change_link = True
    fields = ('name', 'trip_type', 'status', 'start_date', 'end_date')
    readonly_fields = ('name', 'trip_type', 'status', 'start_date', 'end_date')
    can_delete = False
    tab = True
    show_count = True


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        'pk', 'email', 'role', 'full_name',
        'is_email_verified', 'is_subscribed',
        'is_active', 'is_superuser'
    )
    list_filter = (
        'email', 'full_name',
        'is_email_verified', 'is_subscribed',
        'is_active', 'is_staff', 'is_superuser'
    )
    search_fields = ('email', 'full_name')
    ordering = ('id',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    inlines = [TripInline]


# @admin.register(Notification)
# class NotificationAdmin(ModelAdmin):
#     list_display = (
#         'id', 'user', 'type', 'title', 'is_read', 'created_at'
#     )
#     list_filter = ('type', 'is_read', 'created_at')
#     search_fields = ('user__email', 'title', 'body')
#     ordering = ('-created_at',)
#     readonly_fields = ('created_at', 'updated_at', 'deleted_at')


# @admin.register(NotificationSetting)
# class NotificationSettingAdmin(ModelAdmin):
#     list_display = (
#         'id', 'user', 'enabled', 'packing_reminders',
#         'milestone_achievements', 'weekly_summaries'
#     )
#     list_filter = (
#         'enabled', 'packing_reminders',
#         'milestone_achievements', 'weekly_summaries'
#     )
#     search_fields = ('user__email',)
#     readonly_fields = ('created_at', 'updated_at', 'deleted_at')


# @admin.register(UserSubscriptionHistory)
# class UserSubscriptionHistoryAdmin(ModelAdmin):
#     list_display = (
#         'id', 'user', 'product_id', 'subscription_status', 'status', 'start_time', 'expiry_time'
#     )
#     list_filter = ('subscription_status', 'status', 'start_time', 'expiry_time')
#     search_fields = ('user__email', 'product_id', 'order_id')
#     readonly_fields = ('created_at', 'updated_at', 'deleted_at')


# Unregister simplejwt token blacklist models
try:
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
    for model in [OutstandingToken, BlacklistedToken]:
        try:
            admin.site.unregister(model)
        except admin.sites.NotRegistered:
            pass
except ImportError:
    pass

# Unregister django_celery_beat models
try:
    from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule, PeriodicTasks
    for model in [PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule, PeriodicTasks]:
        try:
            admin.site.unregister(model)
        except admin.sites.NotRegistered:
            pass
except ImportError:
    pass
