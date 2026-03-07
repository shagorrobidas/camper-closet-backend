from django.contrib import admin
from closet.models import BrandCategoryType, ItemCategory, ClosetItem


class ItemCategoryInline(admin.TabularInline):
    model = ItemCategory
    extra = 1
    autocomplete_fields = ("user", "type")


class ClosetItemInline(admin.TabularInline):
    model = ClosetItem
    extra = 1
    autocomplete_fields = ("user", "category")


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
    inlines = [ItemCategoryInline]


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
    inlines = [ClosetItemInline]


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