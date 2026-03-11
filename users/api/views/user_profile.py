from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import User
from users.permission import ProfileAccessMixin
from users.api.serializers import UserSerializer, ChildSerializer
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler


class UserProfileView(ProfileAccessMixin, generics.RetrieveAPIView):
    """
    Retrieve user profile.
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user()
            serializer = self.get_serializer(user)
            data = serializer.data

            if user.role == 'parent':
                data['child'] = ChildSerializer(
                    user.children.all(),
                    many=True,
                    context={'request': request},
                ).data
            elif user.role == 'child' and user.parent:
                data['parent'] = UserSerializer(
                    user.parent,
                    context={'request': request},
                ).data

            return CustomResponse.success(
                data=data,
                message="User profile retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class UpdateUserProfileView(ProfileAccessMixin, generics.UpdateAPIView):
    """
    Update user profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user()

            # Use partial=True natively or through standard DRF kwargs
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return CustomResponse.success(
                data=serializer.data,
                message="User profile updated successfully.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class DeleteUserProfileView(ProfileAccessMixin, generics.DestroyAPIView):
    """
    Delete user profile.
    Note: Deleting a parent automatically cascades to all their child accounts.
    """
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user()
            user.delete()
            return CustomResponse.success(
                message="User profile deleted successfully.",
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return custom_exception_handler(e, request)
