from rest_framework import serializers
from packing.models import PackingTemplateCategory

class PackingTemplateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackingTemplateCategory
        fields = [
            'id',
            'template',
            'name',
            'sort_order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]
