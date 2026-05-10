from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from closet.models import ItemCategoryType, ItemCategory, ClosetItem


class ItemCategoryInline(TabularInline):
    model = ItemCategory
    extra = 1
    autocomplete_fields = ("type",)


class ClosetItemInline(TabularInline):
    model = ClosetItem
    extra = 1
    autocomplete_fields = ("user", "main_category", "sub_category")


@admin.register(ItemCategoryType)
class ItemCategoryTypeAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "code")
    ordering = ("name",)
    inlines = [ItemCategoryInline]


@admin.register(ItemCategory)
class ItemCategoryAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "type",
        "is_custom",
        "is_system",
        "created_at",
    )
    list_filter = (
        "type",
        "is_custom",
        "is_system",
        "created_at",
    )
    search_fields = (
        "name",
        "user__email",
    )
    autocomplete_fields = ("type", "user")
    ordering = ("-created_at",)
    inlines = [ClosetItemInline]


@admin.register(ClosetItem)
class ClosetItemAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "main_category",
        "sub_category",
        "brand",
        "quantity",
        "is_scanned",
        "is_favorite",
        "created_at",
    )
    list_filter = (
        "main_category",
        "sub_category",
        "is_scanned",
        "is_favorite",
        "created_at",
    )
    search_fields = (
        "name",
        "brand",
        "color",
        "user__email",
        "user__full_name",
    )
    autocomplete_fields = ("user", "main_category", "sub_category")
    ordering = ("-created_at",)