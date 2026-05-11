from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SiteConfiguration, ContactMessage, Testimonial


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(ModelAdmin):
    fieldsets = (
        ('Social Links & App Store', {
            'fields': (
                'facebook_url', 'linkedin_url', 'twitter_url', 'email_address',
                'app_store_url', 'play_store_url'
            )
        }),
        ('Stats Section', {
            'fields': (
                'stat_downloads_value',
                'stat_members_value',
                'stat_communities_value'
            )
        }),
        ('Hero Section', {
            'fields': (
                'hero_title',
                'hero_subtitle_blue',
                'hero_description',
                'hero_desktop_image',
                'hero_mobile_frame_image'
            )
        }),
        ('Features Section', {
            'fields': (
                'features_section_title',
                'feature_1_title',
                'feature_1_description',
                'feature_1_image',
                'feature_2_title', 'feature_2_description', 'feature_2_image'
            )
        }),
        ('Dynamic Packing Section', {
            'fields': (
                'packing_section_title',
                'packing_section_description',
                'packing_section_image'
            )
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

    def has_add_permission(self, request):
        if self.model.objects.count() > 0:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at', 'updated_at', 'deleted_at')

    def has_add_permission(self, request):
        return False


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = (
        'author_name', 'author_role', 'rating', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'rating')
    search_fields = ('author_name', 'text')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
