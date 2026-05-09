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
    brand_category_name = serializers.CharField(
        source='brand_category.name', read_only=True
    )
    shop_urls = serializers.SerializerMethodField()

    class Meta:
        model = PackingTemplateItem
        fields = [
            'id',
            'template',
            'main_category',
            'main_category_name',
            'sub_category',
            'sub_category_name',
            'brand_category',
            'brand_category_name',
            'title',
            'quantity',
            'is_required',
            'show_shop_url',
            'shop_urls',
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

    def get_shop_urls(self, obj):
        if obj.show_shop_url and obj.brand_category:
            return list(obj.brand_category.shop_websites.filter(
                is_active=True
            ).values_list('website_url', flat=True))
        return []

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not instance.show_shop_url:
            ret.pop('shop_urls', None)
        return ret


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
