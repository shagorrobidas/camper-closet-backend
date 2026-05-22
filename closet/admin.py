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
    readonly_fields = ("created_at", "updated_at", "deleted_at")
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
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    inlines = [ClosetItemInline]


@admin.register(ClosetItem)
class ClosetItemAdmin(ModelAdmin):
    list_display = (
        "closet_item_name",
        "user_email",
        "main_category_name",
        "sub_category_name",
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
    readonly_fields = ("created_at", "updated_at", "deleted_at")

    @admin.display(description="User email")
    def user_email(self, obj):
        return obj.user.email if obj.user else "None"

    @admin.display(description="Main category name")
    def main_category_name(self, obj):
        return obj.main_category.name if obj.main_category else "None"

    @admin.display(description="Sub category name")
    def sub_category_name(self, obj):
        return obj.sub_category.name if obj.sub_category else "None"

    @admin.display(description="Closet item name")
    def closet_item_name(self, obj):
        return obj.name