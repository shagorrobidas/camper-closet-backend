from django.contrib import admin
from packing.models import (
    TripType, Trip,
    PackingTemplate, PackingTemplateItem, PackingTemplateCategory,
    TripPackingItem, TripPackingItemSelection, TripEvent
)


@admin.register(TripType)
class TripTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


class PackingTemplateItemInline(admin.TabularInline):
    model = PackingTemplateItem
    extra = 1
    raw_id_fields = ('category',)


class PackingTemplateCategoryInline(admin.TabularInline):
    model = PackingTemplateCategory
    extra = 1


@admin.register(PackingTemplateCategory)
class PackingTemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'sort_order')
    list_filter = ('template',)
    search_fields = ('name', 'template__title')


@admin.register(PackingTemplate)
class PackingTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'trip_type',
        'season',
        'is_system',
        'is_active',
        'sort_order',
        'created_at'
    )
    list_filter = (
        'trip_type',
        'season',
        'is_system',
        'is_active'
    )
    search_fields = ('title', 'description')
    inlines = [PackingTemplateCategoryInline, PackingTemplateItemInline]


@admin.register(PackingTemplateItem)
class PackingTemplateItemAdmin(admin.ModelAdmin):
    list_display = (
        'template',
        'category',
        'brand_category',
        'title',
        'quantity',
        'is_required',
        'show_shop_url',
        'sort_order'
    )
    list_filter = (
        'template',
        'brand_category',
        'is_required',
        'show_shop_url'
    )
    search_fields = (
        'template__title', 'title', 'note',
        'brand_category__name'
    )


class TripPackingItemInline(admin.TabularInline):
    model = TripPackingItem
    extra = 1
    raw_id_fields = (
        'main_category',
        'sub_category',
        'template_item'
    )


class TripEventInline(admin.TabularInline):
    model = TripEvent
    extra = 1


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'user',
        'trip_type',
        'status',
        'is_template_applied',
        'start_date',
        'end_date'
    )
    list_filter = (
        'trip_type',
        'status',
        'is_template_applied',
        'start_date'
    )
    search_fields = ('name', 'location', 'user__email')
    inlines = [TripPackingItemInline, TripEventInline]


class TripPackingItemSelectionInline(admin.TabularInline):
    model = TripPackingItemSelection
    extra = 1
    raw_id_fields = ('closet_item',)


@admin.register(TripPackingItem)
class TripPackingItemAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'trip',
        'status',
        'main_category',
        'sub_category',
        'title',
        'quantity',
        'picked_quantity',
        'is_packed'
    )
    list_filter = (
        'status',
        'main_category',
        'sub_category',
        'is_packed',
        'is_custom_item'
    )
    search_fields = (
        'trip__name',
        'title',
        'note',
        'sub_category__name'
    )
    inlines = [TripPackingItemSelectionInline]
    raw_id_fields = (
        'trip',
        'main_category',
        'sub_category',
        'template_item'
    )


@admin.register(TripPackingItemSelection)
class TripPackingItemSelectionAdmin(admin.ModelAdmin):
    list_display = (
        'packing_item',
        'closet_item',
        'quantity'
    )
    raw_id_fields = (
        'packing_item',
        'closet_item'
    )


@admin.register(TripEvent)
class TripEventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'trip',
        'event_type',
        'date'
    )
