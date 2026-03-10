from rest_framework import serializers
from packing.models import PackingTemplate, PackingTemplateItem
from django.db.models import Sum


class PackingTemplateItemSerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(
        source='main_category.name', read_only=True
    )
    sub_category_name = serializers.CharField(
        source='sub_category.name', read_only=True
    )

    class Meta:
        model = PackingTemplateItem
        fields = [
            'id',
            'template',
            'main_category',
            'main_category_name',
            'sub_category',
            'sub_category_name',
            'title',
            'quantity',
            'is_required',
            'note',
            'sort_order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class PackingTemplateSerializer(serializers.ModelSerializer):
    total_items = serializers.SerializerMethodField()
    trip_type_name = serializers.CharField(
        source='trip_type.name', read_only=True
    )

    class Meta:
        model = PackingTemplate
        fields = [
            'id',
            'title',
            'trip_type',
            'trip_type_name',
            'season',
            'description',
            'image',
            'is_system',
            'is_active',
            'sort_order',
            'total_items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'is_system',
            'created_at',
            'updated_at',
        ]

    def get_total_items(self, obj):
        return obj.items.aggregate(total=Sum('quantity'))['total'] or 0


class PackingTemplateDetailSerializer(PackingTemplateSerializer):
    items = PackingTemplateItemSerializer(many=True, read_only=True)

    class Meta(PackingTemplateSerializer.Meta):
        fields = PackingTemplateSerializer.Meta.fields + ['items']
