from rest_framework import serializers
from django.contrib.auth import authenticate


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
        user = authenticate(
            request=self.context.get('request'),
            email=email, password=password
        )

        if not user:
            raise serializers.ValidationError({
                "message": "Invalid email or password",
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