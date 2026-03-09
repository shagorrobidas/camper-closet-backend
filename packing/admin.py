from django.contrib import admin
from packing.models import (
    TripType, TripStatus, Trip,
    PackingTemplateSeason, PackingTemplate,
    PackingTemplateCategory, PackingTemplateItem,
    PackingList, PackingListItem
)


@admin.register(TripType)
class TripTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


@admin.register(TripStatus)
class TripStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'sort_order', 'is_final', 'created_at')
    list_editable = ('sort_order', 'is_final')
    search_fields = ('name', 'code')


class PackingTemplateCategoryInline(admin.TabularInline):
    model = PackingTemplateCategory
    extra = 1
    sortable_field_name = "sort_order"


@admin.register(PackingTemplate)
class PackingTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip_type', 'season', 'sort_order', 'created_at')
    list_filter = ('trip_type', 'season')
    search_fields = ('title', 'description')
    inlines = [PackingTemplateCategoryInline]


class PackingTemplateItemInline(admin.TabularInline):
    model = PackingTemplateItem
    extra = 1
    sortable_field_name = "sort_order"


@admin.register(PackingTemplateCategory)
class PackingTemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'item_category', 'sort_order')
    list_filter = ('template', 'item_category')
    search_fields = ('name',)
    inlines = [PackingTemplateItemInline]


@admin.register(PackingTemplateItem)
class PackingTemplateItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_category', 'quantity', 'is_required', 'sort_order')
    list_filter = ('template_category__template', 'is_required')
    search_fields = ('name', 'note')


class PackingListItemInline(admin.TabularInline):
    model = PackingListItem
    extra = 1


@admin.register(PackingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'created_at')
    search_fields = ('title', 'trip__name')
    inlines = [PackingListItemInline]


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'trip_type', 'status', 'start_date', 'end_date')
    list_filter = ('trip_type', 'status', 'start_date')
    search_fields = ('name', 'location', 'user__email')


@admin.register(PackingTemplateSeason)
class PackingTemplateSeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'sort_order', 'created_at')
    list_editable = ('sort_order',)
    search_fields = ('name', 'code')


@admin.register(PackingListItem)
class PackingListItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'packing_list', 'quantity', 'is_packed', 'is_custom_item')
    list_filter = ('is_packed', 'is_custom_item')
    search_fields = ('name', 'closet_item__name', 'note')
