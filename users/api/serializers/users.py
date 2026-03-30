from rest_framework import serializers
from users.models import User
from .child import ChildSerializer


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'role',
            'full_name',
            'profile_pic',
            'date_of_birth',
            'parent',
            'is_email_verified',
            'created_at'
        )
        read_only_fields = (
            'id',
            'is_email_verified',
            'created_at'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.profile_pic:
            request = self.context.get('request')
            if request:
                ret['profile_pic'] = request.build_absolute_uri(
                    instance.profile_pic.url
                )
            else:
                ret['profile_pic'] = instance.profile_pic.url
        return ret


class ManageAccountSerializer(serializers.ModelSerializer):
    children = ChildSerializer(many=True, read_only=True)
    total_child = serializers.SerializerMethodField()
    # parent = UserSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'role',
            'full_name',
            'profile_pic',
            'date_of_birth',
            # 'parent',
            'children',
            'total_child',
            'is_email_verified',
            'created_at'
        )
        read_only_fields = (
            'id',
            'is_email_verified',
            'created_at'
        )

    def get_total_child(self, obj):
        return obj.children.count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.profile_pic:
            request = self.context.get('request')
            if request:
                ret['profile_pic'] = request.build_absolute_uri(
                    instance.profile_pic.url
                )
            else:
                ret['profile_pic'] = instance.profile_pic.url

        # Restructure response as requested
        children = ret.pop('children', [])
        total_child = ret.pop('total_child', 0)

        return {
            'total_child': total_child,
            'my_account': ret,
            'child_accounts': children
        }