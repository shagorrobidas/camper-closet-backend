from rest_framework import serializers
from packing.models import Trip, PackingClosetItem


class PackingClosetItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='template_item.sub_category.name',
        read_only=True
    )
    closet_item_names = serializers.SerializerMethodField()

    class Meta:
        model = PackingClosetItem
        fields = [
            'id',
            'trip',
            'status',
            'template_item',
            'closet_item',
            'closet_item_names',
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

    def get_closet_item_names(self, obj):
        return [item.name for item in obj.closet_item.all()]


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
    packing_items = PackingClosetItemSerializer(many=True, read_only=True)

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ['packing_items']
