from rest_framework import serializers
from closet.models import ClosetItem


class ClosetItemSerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(
        source='main_category.name', read_only=True
    )
    sub_category_name = serializers.CharField(
        source='sub_category.name', read_only=True
    )

    class Meta:
        model = ClosetItem
        fields = [
            'id',
            'user',
            'main_category',
            'main_category_name',
            'sub_category',
            'sub_category_name',
            'name',
            'image',
            'brand',
            'color',
            'size',
            'quantity',
            'notes',
            'is_scanned',
            'is_favorite',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'is_scanned',
            'sub_category_name',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        
        # 1. Auto-pick main_category from sub_category
        sub_category = attrs.get('sub_category')
        main_category = attrs.get('main_category')
        if sub_category and not main_category:
            attrs['main_category'] = sub_category.type



        return attrs
