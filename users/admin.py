from django.contrib import admin
from django import forms
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
from closet.models import ClosetItem


from django.utils.safestring import mark_safe

class TogglePasswordInput(forms.PasswordInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        import uuid
        btn_id = f"toggle-btn-{uuid.uuid4().hex[:8]}"
        input_id = attrs.get('id') or f"id_{name}"
        
        toggle_html = f"""
        <div class="flex flex-col gap-1 w-full max-w-lg">
            {html}
            <div class="flex items-center gap-2 mt-1">
                <input type="checkbox" id="{btn_id}" class="rounded border-slate-300 dark:border-slate-800 text-indigo-600 focus:ring-indigo-500 cursor-pointer" />
                <label for="{btn_id}" class="text-xs font-semibold text-slate-500 dark:text-slate-400 cursor-pointer select-none">Show password</label>
            </div>
        </div>
        <script>
            (function() {{
                const checkbox = document.getElementById('{btn_id}');
                const input = document.getElementById('{input_id}');
                if (checkbox && input) {{
                    checkbox.addEventListener('change', function() {{
                        input.type = checkbox.checked ? 'text' : 'password';
                    }});
                }}
            }})();
        </script>
        """
        return mark_safe(toggle_html)


class UserAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        label="Change Password",
        required=False,
        widget=TogglePasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text="Leave blank if you do not want to change the user's password."
    )

    class Meta:
        model = User
        fields = '__all__'


class TripInline(TabularInline):
    model = Trip
    extra = 0
    show_change_link = True
    fields = ('name', 'trip_type', 'status', 'start_date', 'end_date', 'total_quantity', 'packed_quantity')
    readonly_fields = ('name', 'trip_type', 'status', 'start_date', 'end_date', 'total_quantity', 'packed_quantity')
    can_delete = False
    tab = True
    show_count = True

    def total_quantity(self, obj):
        from django.db.models import Sum
        val = obj.packing_items.aggregate(total=Sum('quantity'))['total']
        return val or 0
    total_quantity.short_description = "Total Quantity"

    def packed_quantity(self, obj):
        from django.db.models import Sum
        val = obj.packing_items.aggregate(total=Sum('picked_quantity'))['total']
        return val or 0
    packed_quantity.short_description = "Packed Quantity"


class UserPackingTemplateInline(TabularInline):
    model = Trip
    verbose_name = "Camp Template"
    verbose_name_plural = "Camp Templates"
    extra = 0
    show_change_link = True
    fields = ('trip_name', 'template_link', 'template_trip_type', 'template_season', 'template_total_quantity')
    readonly_fields = ('trip_name', 'template_link', 'template_trip_type', 'template_season', 'template_total_quantity')
    can_delete = False
    tab = True
    show_count = True

    def get_queryset(self, request):
        return super().get_queryset(request).filter(template__isnull=False).select_related('template')

    def trip_name(self, obj):
        return obj.name
    trip_name.short_description = "Camper Name"

    def template_link(self, obj):
        from django.utils.safestring import mark_safe
        if obj.template:
            url = f"/admin/packing/packingtemplate/{obj.template.id}/change/"
            return mark_safe(f'<a href="{url}" class="text-indigo-600 hover:text-indigo-900 font-bold hover:underline">{obj.template.title}</a>')
        return "None"
    template_link.short_description = "Camp Template"

    def template_trip_type(self, obj):
        return obj.template.trip_type.name if obj.template and obj.template.trip_type else "None"
    template_trip_type.short_description = "Camp Type"

    def template_season(self, obj):
        return obj.template.season if obj.template else "None"
    template_season.short_description = "Season"

    def template_total_quantity(self, obj):
        from django.db.models import Sum
        if obj.template:
            val = obj.template.items.aggregate(total=Sum('quantity'))['total']
            return val or 0
        return 0
    template_total_quantity.short_description = "Total Quantity"


class ClosetItemInline(TabularInline):
    model = ClosetItem
    verbose_name = "Closet Item"
    verbose_name_plural = "Closet Items"
    extra = 0
    show_change_link = True
    fields = ('name', 'main_category', 'sub_category', 'brand', 'size', 'quantity', 'is_favorite')
    readonly_fields = ('name', 'main_category', 'sub_category', 'brand', 'size', 'quantity', 'is_favorite')
    can_delete = False
    tab = True
    show_count = True


@admin.register(User)
class UserAdmin(ModelAdmin):
    form = UserAdminForm
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
    inlines = [TripInline, UserPackingTemplateInline, ClosetItemInline]

    def save_model(self, request, obj, form, change):
        new_pass = form.cleaned_data.get('new_password')
        if new_pass:
            obj.set_password(new_pass)
        super().save_model(request, obj, form, change)


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
