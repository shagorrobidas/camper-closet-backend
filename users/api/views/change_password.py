from rest_framework import generics, permissions, status, serializers
from users.api.serializers import ChangePasswordSerializer
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash

User = get_user_model()


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            if not user.check_password(old_password):
                return CustomResponse.error(
                    message="Current password is incorrect",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return CustomResponse.success(
                message='Password changed successfully',
                status_code=status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            return custom_exception_handler(e, request)
        except Exception as e:
            return custom_exception_handler(e, request)