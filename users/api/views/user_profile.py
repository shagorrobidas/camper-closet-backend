from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from users.models import User
from users.api.serializers import UserSerializer
from core.utils.response import CustomResponse
from core.utils.exceptions import custom_exception_handler


class ProfileAccessMixin:
    """
    Provides object-level permissions for user profiles.
    - If no PK is provided, returns the authenticated user's profile.
    - If a PK is provided, allows access if:
        1. The requested PK is the authenticated user.
        2. The authenticated user is a parent, and the requested PK is their child.
    """
    def get_object(self):
        pk = self.kwargs.get('pk')
        
        # Operate on self if no specific ID requested
        if not pk:
            return self.request.user

        user = get_object_or_404(User, pk=pk)
        
        # User accessing their own profile
        if user == self.request.user:
            return user
            
        # Parent accessing their child's profile
        if self.request.user.role == 'parent' and user.parent == self.request.user:
            return user
            
        raise PermissionDenied("You do not have permission to access this profile.")


class UserProfileView(ProfileAccessMixin, generics.RetrieveAPIView):
    """
    Retrieve user profile.
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)
            return CustomResponse.success(
                data=serializer.data,
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
            user = self.get_object()
            
            # Use partial=True natively or through standard DRF kwargs
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(user, data=request.data, partial=partial)
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
            user = self.get_object()
            user.delete()
            return CustomResponse.success(
                message="User profile deleted successfully.",
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return custom_exception_handler(e, request)