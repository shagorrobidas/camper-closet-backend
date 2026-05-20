from django.contrib import admin
from unfold.admin import ModelAdmin
from dashboard.models import BrandCategory, ShopWebsite


@admin.register(BrandCategory)
class BrandCategoryAdmin(ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(ShopWebsite)
class ShopWebsiteAdmin(ModelAdmin):
    list_display = ('id', 'name', 'website_url', 'is_active')
    list_filter = ('is_active', 'categories')
    search_fields = ('name', 'description')
    ordering = ('name',)
    filter_horizontal = ('categories',)