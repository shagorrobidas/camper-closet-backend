from rest_framework import serializers
from closet.models import ItemCategoryType, ItemCategory


class ClosetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategoryType
        fields = [
            'id',
            'name'
        ]
        read_only_fields = [
            'id',
        ]


class ClosetCategoryDetailSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = ItemCategoryType
        fields = [
            'id',
            'name',
            'subcategories',
        ]

    def get_subcategories(self, instance):
        user = self.context.get('user')
        from django.db.models import Q
        qs = ItemCategory.objects.filter(type=instance)
        if user:
            qs = qs.filter(Q(is_system=True) | Q(user=user))
        else:
            qs = qs.filter(is_system=True)
        return [{'id': str(cat.id), 'name': cat.name} for cat in qs]


class ClosetSubCategorySerializer(serializers.ModelSerializer):
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemCategoryType.objects.all(),
        source='type',
        write_only=True
    )

    class Meta:
        model = ItemCategory
        fields = [
            'id',
            'name',
            'type',
            'type_id',
        ]
        read_only_fields = [
            'id',
            'type',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('type', None)
        if instance.type:
            ret['category'] = {
                'id': str(instance.type.id),
                'name': instance.type.name,
            }
        return ret
