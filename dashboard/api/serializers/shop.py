from rest_framework import serializers
from dashboard.models import ShopWebsite, BrandCategory


class BrandCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandCategory
        fields = [
            'id',
            'name',
        ]


class ShopWebsiteSerializer(serializers.ModelSerializer):
    categories = BrandCategorySerializer(many=True, read_only=True)

    class Meta:
        model = ShopWebsite
        fields = [
            'id',
            'name',
            'description',
            'website_url',
            'categories',
            'image',
            'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']