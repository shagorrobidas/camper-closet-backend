from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from packing.models import (
    TripType, Trip,
    PackingTemplate, PackingTemplateItem, PackingTemplateCategory,
    TripPackingItem, TripPackingItemSelection, TripEvent
)


@admin.register(TripType)
class TripTypeAdmin(ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)


class PackingTemplateItemInline(TabularInline):
    model = PackingTemplateItem
    extra = 1
    exclude = ('deleted_at',)
    # raw_id_fields = ('category',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            import re
            match = re.search(r'packingtemplate/([^/]+)/change', request.path)
            if match:
                template_id = match.group(1)
                kwargs["queryset"] = PackingTemplateCategory.objects.filter(template_id=template_id)
            else:
                kwargs["queryset"] = PackingTemplateCategory.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PackingTemplateCategoryInline(TabularInline):
    model = PackingTemplateCategory
    extra = 1
    exclude = ('deleted_at',)


@admin.register(PackingTemplateCategory)
class PackingTemplateCategoryAdmin(ModelAdmin):
    list_display = ('name', 'template', 'sort_order')
    list_filter = ('template',)
    search_fields = ('name', 'template__title')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)


@admin.register(PackingTemplate)
class PackingTemplateAdmin(ModelAdmin):
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
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(PackingTemplateItem)
class PackingTemplateItemAdmin(ModelAdmin):
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
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            import re
            match = re.search(r'packingtemplateitem/([^/]+)/change', request.path)
            if match:
                item_id = match.group(1)
                item = self.model.objects.filter(id=item_id).first()
                if item:
                    kwargs["queryset"] = PackingTemplateCategory.objects.filter(template=item.template)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TripPackingItemInline(TabularInline):
    model = TripPackingItem
    extra = 1
    raw_id_fields = (
        'main_category',
        'sub_category',
        'template_item'
    )


class TripEventInline(TabularInline):
    model = TripEvent
    extra = 1


@admin.register(Trip)
class TripAdmin(ModelAdmin):
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
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)


class TripPackingItemSelectionInline(TabularInline):
    model = TripPackingItemSelection
    extra = 1
    raw_id_fields = ('closet_item',)


@admin.register(TripPackingItem)
class TripPackingItemAdmin(ModelAdmin):
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
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)


@admin.register(TripPackingItemSelection)
class TripPackingItemSelectionAdmin(ModelAdmin):
    list_display = (
        'packing_item',
        'closet_item',
        'quantity'
    )
    raw_id_fields = (
        'packing_item',
        'closet_item'
    )
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)


@admin.register(TripEvent)
class TripEventAdmin(ModelAdmin):
    list_display = (
        'title',
        'trip',
        'event_type',
        'date'
    )
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('deleted_at',)
