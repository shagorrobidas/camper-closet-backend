from django.contrib import admin
from packing.models import (
    TripType, Trip,
    PackingTemplate, PackingTemplateItem,
    PackingClosetItem
)


@admin.register(TripType)
class TripTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


@admin.register(PackingTemplate)
class PackingTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'trip_type', 'season', 'sort_order', 'created_at'
    )
    list_filter = ('trip_type', 'season')
    search_fields = ('title', 'description')


class PackingTemplateItemInline(admin.TabularInline):
    model = PackingTemplateItem
    extra = 1


@admin.register(PackingTemplateItem)
class PackingTemplateItemAdmin(admin.ModelAdmin):
    list_display = (
        'template', 'main_category', 'sub_category',
        'quantity', 'is_required'
    )
    list_filter = (
        'template', 'main_category', 'sub_category', 'is_required'
    )
    search_fields = (
        'template__title', 'note',
        'main_category__name', 'sub_category__name'
    )


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'trip_type', 'status', 'start_date', 'end_date'
    )
    list_filter = ('trip_type', 'status', 'start_date')
    search_fields = ('name', 'location', 'user__email')


@admin.register(PackingClosetItem)
class PackingClosetItemAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'trip', 'status', 'quantity', 'picked_quantity', 'is_packed'
    )
    list_filter = ('status', 'is_packed', 'is_custom_item')
    search_fields = ('trip__name', 'note', 'template_item__sub_category__name')
    filter_horizontal = ('closet_item',)
