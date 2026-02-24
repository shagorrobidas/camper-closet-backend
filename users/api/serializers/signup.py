from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'password_confirm',
            'full_name',
            'date_of_birth',
            
        )

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "message": "Passwords don't match",
                "code": "400"
            })
        
        # Enforce strong password
        try:
            validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                "message": " ".join(e.messages),
                "code": "400"
            })

        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "error": "A user with this email already exists",
                "code": "400"
            })
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
        )
        return user
