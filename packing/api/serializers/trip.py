from rest_framework import serializers
from packing.models import Trip, PackingList, PackingListItem


class PackingListItemSerializer(serializers.ModelSerializer):
    closet_item_name = serializers.CharField(source='closet_item.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = PackingListItem
        fields = [
            'id',
            'packing_list',
            'template_item',
            'closet_item',
            'closet_item_name',
            'category',
            'category_name',
            'quantity',
            'picked_quantity',
            'is_packed',
            'packed_at',
            'is_custom_item',
            'note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PackingListSerializer(serializers.ModelSerializer):
    items = PackingListItemSerializer(many=True, read_only=True)

    class Meta:
        model = PackingList
        fields = [
            'id',
            'trip',
            'title',
            'status',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            'id',
            'user',
            'template',
            'trip_type',
            'status',
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
            'created_at',
            'updated_at',
        ]


class TripDetailSerializer(TripSerializer):
    packing_list = PackingListSerializer(read_only=True)

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ['packing_list']