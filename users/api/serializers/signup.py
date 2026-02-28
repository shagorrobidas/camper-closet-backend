from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from users.models import User


# ── Shared mixin ────────────────────────────────────────────────────────────

class _PasswordMixin:
    """Validates password match and Django password-strength rules."""

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "message": "Passwords don't match.",
                "code": "400"
            })
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
                "message": "A user with this email already exists.",
                "code": "400"
            })
        return value


# ── Parent registration ──────────────────────────────────────────────────────

class RegisterParentSerializer(_PasswordMixin, serializers.ModelSerializer):
    """
    Creates a user with role='parent'.
    No parent_id is accepted — parents are top-level accounts.
    """
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

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_parent(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            date_of_birth=validated_data.get('date_of_birth'),
        )
        return user


# ── Child registration ───────────────────────────────────────────────────────

class RegisterChildSerializer(_PasswordMixin, serializers.ModelSerializer):
    """
    Creates a user with role='child', linked to an existing parent account.
    The authenticated parent is injected by the view; clients cannot supply
    an arbitrary parent_id.
    """
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

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        parent = self.context['parent']
        user = User.objects.create_child(
            email=validated_data['email'],
            password=validated_data['password'],
            parent=parent,
            full_name=validated_data.get('full_name', ''),
            date_of_birth=validated_data.get('date_of_birth'),
        )
        # Children are verified immediately — the parent registers them,
        # so no email OTP step is required.
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return user



