from rest_framework import serializers
from packing.models import (
    Trip,
    TripPackingItem,
    TripPackingItemSelection,
    TripType,
    PackingTemplateCategory
)
from django.db.models import Sum, Q
from django.db import models
from django.utils import timezone


class TripPackingItemSelectionSerializer(serializers.ModelSerializer):
    closet_item_name = serializers.CharField(
        source='closet_item.name', read_only=True
    )
    closet_item_image = serializers.ImageField(
        source='closet_item.image', read_only=True
    )

    class Meta:
        model = TripPackingItemSelection
        fields = [
            'id',
            'packing_item',
            'closet_item',
            'closet_item_name',
            'closet_item_image',
            'quantity',
            'note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TripPackingItemSerializer(serializers.ModelSerializer):
    selections = TripPackingItemSelectionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(
        source='template_item.category.name', read_only=True, allow_null=True
    )
    category_id = serializers.UUIDField(
        source='template_item.category.id', read_only=True, allow_null=True
    )
    shop_urls = serializers.SerializerMethodField()
    show_shop_url = serializers.SerializerMethodField()

    class Meta:
        model = TripPackingItem
        fields = [
            'id',
            'trip',
            'category_name',
            'category_id',
            'title',
            'status',
            'template_item',
            'selections',
            'quantity',
            'picked_quantity',
            'remaining_quantity',
            'is_required',
            'is_packed',
            'packed_at',
            'is_custom_item',
            'show_shop_url',
            'shop_urls',
            'note',
            'sort_order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'trip',
            'template_item',
            'picked_quantity',
            'remaining_quantity',
            'is_packed',
            'packed_at',
            'created_at',
            'updated_at',
        ]

    def get_show_shop_url(self, obj):
        if obj.template_item:
            return obj.template_item.show_shop_url
        return False

    def get_shop_urls(self, obj):
        # noqa
        if obj.template_item and obj.template_item.show_shop_url and obj.template_item.brand_category: # noqa
            return list(obj.template_item.brand_category.shop_websites.filter(
                is_active=True
            ).values_list('website_url', flat=True))
        return []

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not (
            instance.template_item and instance.template_item.show_shop_url
        ):
            ret.pop('shop_urls', None)
        return ret


class TripPackingItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPackingItem
        fields = [
            'main_category',
            'sub_category',
            'title',
            'quantity',
            'is_required',
            'note',
            'sort_order',
        ]


class TripStatisticsSerializer(serializers.Serializer):
    active_trips = serializers.SerializerMethodField()
    completed_trips = serializers.SerializerMethodField()
    past_trips = serializers.SerializerMethodField()
    total_trips = serializers.SerializerMethodField()

    def get_active_trips(self, obj):
        today = timezone.now().date()
        return obj.trips.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='Active'
        ).count()

    def get_completed_trips(self, obj):
        return obj.trips.filter(
            status='Complete'
        ).count()

    def get_past_trips(self, obj):
        today = timezone.now().date()
        return obj.trips.filter(
            end_date__lt=today,
            status='Active'
        ).count()

    def get_total_trips(self, obj):
        return obj.trips.count()


class TripSerializer(serializers.ModelSerializer):
    trip_type_name = serializers.CharField(
        source='trip_type.name', read_only=True
    )

    class Meta:
        model = Trip
        fields = [
            'id',
            'user',
            'template',
            'trip_type',
            'trip_type_name',
            'status',
            'is_template_applied',
            'name',
            'location',
            'start_date',
            'end_date',
            'packing_deadline',
            'note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'is_template_applied',
            'created_at',
            'updated_at',
        ]


class TripPackingCategorySerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='name')
    packing_items = serializers.SerializerMethodField()

    class Meta:
        model = PackingTemplateCategory
        fields = ['id', 'category', 'sort_order', 'packing_items']

    def get_packing_items(self, obj):
        trip = self.context.get('trip')
        if not trip:
            return []
        items = TripPackingItem.objects.filter(
            trip=trip,
            template_item__category=obj,
            status='active'
        ).order_by('sort_order')
        return TripPackingItemSerializer(
            items,
            many=True,
            context=self.context
        ).data


class TripDetailSerializer(TripSerializer):
    items = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ['items', 'progress']

    def get_items(self, obj):
        # Get categories from the template
        categories = []
        if obj.template:
            categories = list(obj.template.categories.all().order_by('sort_order'))
        
        # Serialize existing categories
        context = self.context.copy()
        context['trip'] = obj
        serialized_data = TripPackingCategorySerializer(
            categories, many=True, context=context
        ).data

        # Handle items without a category (custom items or items with null category)
        # We include items where template_item is null OR template_item.category is null
        uncategorized_items = obj.packing_items.filter(
            status='active'
        ).filter(
            Q(template_item__isnull=True) | Q(template_item__category__isnull=True)
        ).order_by('sort_order')

        if uncategorized_items.exists():
            serialized_data.append({
                "id": None,
                "category": "Uncategorized",
                "sort_order": 999,
                "packing_items": TripPackingItemSerializer(
                    uncategorized_items, many=True, context=self.context
                ).data
            })

        return serialized_data

    def get_progress(self, obj):
        packing_items = obj.packing_items.filter(status='active')

        agg = packing_items.aggregate(
            total_qty=Sum('quantity'),
            picked_qty=Sum('picked_quantity'),
        )
        total_qty = agg['total_qty'] or 0
        picked_qty = agg['picked_qty'] or 0
        remaining_qty = max(0, total_qty - picked_qty)

        percentage = (
            round((picked_qty / total_qty) * 100, 1)
            if total_qty > 0 else 0
        )

        return {
            # 'total_items': total_items,
            # 'packed_items': packed_items,
            # 'remaining_items': total_items - packed_items,
            'total_quantity': total_qty,
            'picked_quantity': picked_qty,
            'remaining_quantity': remaining_qty,
            'percentage': percentage,
        }


class TripTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripType
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class ActiveIncompleteTripPackingItemSerializer(serializers.ModelSerializer):
    """Trip-centric: one entry per trip, with nested incomplete
    items and overall progress."""
    trip_type_name = serializers.CharField(
        source='trip_type.name', read_only=True
    )
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id',
            'name',
            'location',
            'start_date',
            'end_date',
            'packing_deadline',
            'trip_type',
            'trip_type_name',
            'status',
            'progress',
        ]

    def get_progress(self, obj):
        packing_items = obj.packing_items.filter(status='active')

        agg = packing_items.aggregate(
            total_qty=Sum('quantity'),
            picked_qty=Sum('picked_quantity'),
        )
        total_qty = agg['total_qty'] or 0
        picked_qty = agg['picked_qty'] or 0
        remaining_qty = max(0, total_qty - picked_qty)

        percentage = (
            round((picked_qty / total_qty) * 100, 1)
            if total_qty > 0 else 0
        )

        return {
            'total_quantity': total_qty,
            'picked_quantity': picked_qty,
            'remaining_quantity': remaining_qty,
            'percentage': percentage,
        }