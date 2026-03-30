from rest_framework import serializers


class SwitchChildSerializer(serializers.Serializer):
    child_id = serializers.UUIDField()
    refresh = serializers.CharField()


class SwitchParentSerializer(serializers.Serializer):
    refresh = serializers.CharField()