from rest_framework import serializers
from closet.models import ClosetItem


from django.contrib.auth import get_user_model

User = get_user_model()


class ClosetItemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ClosetItem
        fields = [
            'id',
            'user',
            'category',
            'name',
            'image',
            'brand',
            'color',
            'size',
            'quantity',
            'note',
            'ai_detected',
            'created_at',
            'updated_at'
        ]
