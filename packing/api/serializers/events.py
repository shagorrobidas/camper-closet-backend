from rest_framework import serializers
from packing.models import TripEvent


class TripEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripEvent
        fields = [
            'id',
            'trip',
            'title',
            'description',
            'event_type',
            'date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'trip', 'created_at', 'updated_at']
