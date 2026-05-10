from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Check if both email and password are provided
        if not email or not password:
            raise serializers.ValidationError({
                "message": "Both email and password are required",
                "code": 400
            })

        # Authenticate the user with the provided credentials
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "message": "User not found",
                "code": 404
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "message": "User account is disabled",
                "code": 400
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                "message": "Password does not match",
                "code": 400
            })

        # Temporarily bypassed for testing/development
        if not user.is_email_verified:
            raise serializers.ValidationError({
                "message": "Please verify your email",
                "code": 400
            })

        data['user'] = user
        return data