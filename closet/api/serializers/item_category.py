from rest_framework import serializers
from closet.models import ItemCategory


from django.contrib.auth import get_user_model

User = get_user_model()


class ItemCategorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = ItemCategory
        fields = [
            'id',
            'user',
            'name',
            'type',
            'created_at',
            'updated_at'
        ]
