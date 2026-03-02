from rest_framework import serializers
from closet.models import ItemCategory


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = [
            'id',
            'user',
            'name',
            'type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
        ]

    # def validate(self, attrs):
    #     user = self.context['request'].user
    #     name = attrs.get('name')
    #     type = attrs.get('type')
    #     if ItemCategory.objects.filter(user=user, name=name, type=type).exists():
    #         raise serializers.ValidationError("Item category already exists")
    #     return attrs