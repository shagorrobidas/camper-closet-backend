from rest_framework import serializers
from packing.models import PackingTemplate, PackingTemplateItem
from django.db.models import Sum


class PackingTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTemplateItem
        fields = [
            'id',
            'template',
            'main_category',
            'sub_category',
            'quantity',
            'is_required',
            'note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.main_category:
            ret['main_category'] = {
                'id': instance.main_category.id,
                'name': instance.main_category.name,
            }
        if instance.sub_category:
            ret['sub_category'] = {
                'id': instance.sub_category.id,
                'name': instance.sub_category.name,
            }
        return ret


class PackingTemplateSerializer(serializers.ModelSerializer):
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = PackingTemplate
        fields = [
            'id',
            'title',
            'trip_type',
            'season',
            'description',
            'image',
            'is_system',
            'total_items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def get_total_items(self, obj):
        return obj.items.aggregate(total=Sum('quantity'))['total'] or 0


class PackingTemplateDetailSerializer(PackingTemplateSerializer):
    items = PackingTemplateItemSerializer(many=True, read_only=True)

    class Meta(PackingTemplateSerializer.Meta):
        fields = PackingTemplateSerializer.Meta.fields + ['items']
