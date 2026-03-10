from django.contrib import admin
from packing.models import (
    TripType, Trip,
    PackingTemplate, PackingTemplateItem,
    TripPackingItem, TripPackingItemSelection, TripEvent
)


@admin.register(TripType)
class TripTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


@admin.register(PackingTemplate)
class PackingTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'trip_type', 'season', 'is_system', 'is_active', 'sort_order', 'created_at'
    )
    list_filter = ('trip_type', 'season', 'is_system', 'is_active')
    search_fields = ('title', 'description')


class PackingTemplateItemInline(admin.TabularInline):
    model = PackingTemplateItem
    extra = 1


@admin.register(PackingTemplateItem)
class PackingTemplateItemAdmin(admin.ModelAdmin):
    list_display = (
        'template', 'main_category', 'sub_category',
        'title', 'quantity', 'is_required', 'sort_order'
    )
    list_filter = (
        'template', 'main_category', 'sub_category', 'is_required'
    )
    search_fields = (
        'template__title', 'title', 'note',
        'main_category__name', 'sub_category__name'
    )


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'trip_type', 'status', 'is_template_applied', 'start_date', 'end_date'
    )
    list_filter = ('trip_type', 'status', 'is_template_applied', 'start_date')
    search_fields = ('name', 'location', 'user__email')


@admin.register(TripPackingItem)
class TripPackingItemAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'trip', 'status', 'main_category', 'sub_category', 'title', 'quantity', 'picked_quantity', 'is_packed'
    )
    list_filter = ('status', 'main_category', 'sub_category', 'is_packed', 'is_custom_item')
    search_fields = ('trip__name', 'title', 'note', 'sub_category__name')


@admin.register(TripPackingItemSelection)
class TripPackingItemSelectionAdmin(admin.ModelAdmin):
    list_display = ('packing_item', 'closet_item', 'quantity')


@admin.register(TripEvent)
class TripEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'event_type', 'date')
