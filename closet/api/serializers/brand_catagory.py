from rest_framework import serializers
from closet.models import ItemCategoryType


class ItemCategoryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategoryType
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