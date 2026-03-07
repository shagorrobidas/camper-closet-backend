from rest_framework import serializers
from closet.models import BrandCategoryType


class BrandCategoryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandCategoryType
        fields = [
            'id',
            'name',
            'code',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]