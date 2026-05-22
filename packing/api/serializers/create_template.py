from rest_framework import serializers
from packing.models import PackingTemplate, PackingTemplateItem
from closet.models import ItemCategory, ItemCategoryType
from django.db import transaction
from django.db.models import Sum


class PackingTemplateItemCreateSerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(required=False, write_only=True)
    sub_category_name = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = PackingTemplateItem
        fields = [
            'id',
            'main_category',
            'main_category_name',
            'sub_category',
            'sub_category_name',
            'title',
            'quantity',
            'is_required',
            'note',
            'sort_order',
        ]
        extra_kwargs = {
            'main_category': {'required': False},
            'sub_category': {'required': False},
        }


class PackingTemplateCreateSerializer(serializers.ModelSerializer):
    items = PackingTemplateItemCreateSerializer(many=True)
    trip_type_name = serializers.CharField(
        source='trip_type.name', read_only=True
    )
    total_items = serializers.SerializerMethodField()

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
            'sort_order',
            'is_system',
            'is_active',
            'total_items',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_items(self, obj):
        return obj.items.aggregate(total=Sum('quantity'))['total'] or 0

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        with transaction.atomic():
            template = PackingTemplate.objects.create(**validated_data)

            for item_data in items_data:
                main_cat = item_data.get('main_category')
                main_cat_name = item_data.get('main_category_name')
                sub_cat = item_data.get('sub_category')
                sub_cat_name = item_data.get('sub_category_name')

                # Handle Main Category (ItemCategoryType)
                if not main_cat and main_cat_name:
                    main_cat, _ = ItemCategoryType.objects.get_or_create(
                        name=main_cat_name,
                        defaults={'code': main_cat_name[:5].upper()}
                    )

                # Handle Sub Category (ItemCategory)
                if main_cat and not sub_cat and sub_cat_name:
                    sub_cat, _ = ItemCategory.objects.get_or_create(
                        name=sub_cat_name,
                        type=main_cat,
                        defaults={'is_system': True}
                    )

                PackingTemplateItem.objects.create(
                    template=template,
                    main_category=main_cat,
                    sub_category=sub_cat,
                    title=item_data.get('title'),
                    quantity=item_data.get('quantity', 0),
                    is_required=item_data.get('is_required', True),
                    note=item_data.get('note'),
                    sort_order=item_data.get('sort_order', 0)
                )
            return template
