from rest_framework import serializers


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class VerifyPasswordResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)