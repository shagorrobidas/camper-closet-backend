from rest_framework import serializers
from packing.models import (
    Trip,
    TripPackingItem,
    TripPackingItemSelection,
    TripType
)
from django.db.models import Sum
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
    main_category_name = serializers.CharField(
        source='main_category.name', read_only=True
    )
    sub_category_name = serializers.CharField(
        source='sub_category.name', read_only=True
    )
    selections = TripPackingItemSelectionSerializer(many=True, read_only=True)
    shop_urls = serializers.SerializerMethodField()
    show_shop_url = serializers.SerializerMethodField()

    class Meta:
        model = TripPackingItem
        fields = [
            'id',
            'trip',
            'main_category',
            'main_category_name',
            'sub_category',
            'sub_category_name',
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
        if obj.template_item and obj.template_item.show_shop_url and obj.template_item.brand_category:
            return list(obj.template_item.brand_category.shop_websites.filter(
                is_active=True
            ).values_list('website_url', flat=True))
        return []

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not (instance.template_item and instance.template_item.show_shop_url): 
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
    active_trips = serializers.SerializerMethodField() # trip startdate start and enddate between current date
    completed_trips = serializers.SerializerMethodField() # if tripe packeing is completed
    past_trips = serializers.SerializerMethodField() # trip enddate is before current date
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


class TripDetailSerializer(TripSerializer):
    packing_items = TripPackingItemSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ['packing_items', 'progress']

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