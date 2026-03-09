from django.contrib import admin
from packing.models import (
    TripType, Trip,
    PackingTemplate,         PackingTemplateItem,
    PackingList, PackingListItem
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


class PackingListItemInline(admin.TabularInline):
    model = PackingListItem
    extra = 1


@admin.register(PackingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'trip__name')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'trip_type', 'status', 'start_date', 'end_date'
    )
    list_filter = ('trip_type', 'status', 'start_date')
    search_fields = ('name', 'location', 'user__email')



@admin.register(PackingListItem)
class PackingListItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quantity', 'is_packed', 'is_custom_item')
    list_filter = ('is_packed', 'is_custom_item')
    search_fields = ('name', 'closet_item__name', 'note')
