from rest_framework import serializers
from users.models import User


class ChildSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(
        required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'role',
            'full_name',
            'profile_pic',
            'date_of_birth',
            'is_email_verified',
            'created_at',
        )
        read_only_fields = (
            'id',
            'is_email_verified',
            'created_at',
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
