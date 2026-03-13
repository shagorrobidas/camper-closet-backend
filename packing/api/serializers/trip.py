from rest_framework import serializers
from packing.models import Trip, TripPackingItem, TripPackingItemSelection


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
        total = packing_items.count()
        packed = packing_items.filter(is_packed=True).count()
        percentage = round((packed / total) * 100, 1) if total > 0 else 0
        return {
            'total_items': total,
            'packed_items': packed,
            'remaining_items': total - packed,
            'percentage': percentage,
        }
