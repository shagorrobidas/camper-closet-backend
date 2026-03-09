from rest_framework import serializers
from closet.models import ItemCategory


class ItemCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemCategory
        fields = [
            'id',
            'users',
            'name',
            'type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'users',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.type:
            ret['type'] = {
                'id': str(instance.type.id),
                'name': instance.type.name,
                'code': instance.type.code,
            }
        return ret
