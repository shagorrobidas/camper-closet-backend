from django.contrib import admin
from closet.models import BrandCategoryType, ItemCategory, ClosetItem


@admin.register(BrandCategoryType)
class BrandCategoryTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "code")
    ordering = ("name",)


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "type",
        "is_custom",
        "created_at",
    )
    list_filter = (
        "type",
        "is_custom",
        "created_at",
    )
    search_fields = (
        "name",
        "user__email",
        "user__full_name",
    )
    autocomplete_fields = ("user", "type")
    ordering = ("-created_at",)


@admin.register(ClosetItem)
class ClosetItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "category",
        "brand",
        "color",
        "size",
        "quantity",
        "ai_detected",
        "created_at",
    )
    list_filter = (
        "category",
        "ai_detected",
        "created_at",
    )
    search_fields = (
        "name",
        "brand",
        "color",
        "user__email",
        "user__full_name",
    )
    autocomplete_fields = ("user", "category")
    ordering = ("-created_at",)