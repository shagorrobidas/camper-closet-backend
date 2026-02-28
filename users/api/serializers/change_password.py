from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        errors = {}

        # Check if new passwords match
        if data['new_password'] != data['confirm_password']:
            errors = {
                "error": "New passwords don't match",
            }

        # Check if new password is different from old password
        if data['old_password'] == data['new_password']:
            errors = {
                "error": "New password must be different from current password", # noqa
            }

        if errors:
            raise serializers.ValidationError(errors)

        return data