from rest_framework import serializers
from closet.models import ClosetItem


class ClosetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClosetItem
        fields = [
            'id',
            'user',
            'category',
            'name',
            'image',
            'brand',
            'color',
            'size',
            'quantity',
            'note',
            'ai_detected',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
        ]
