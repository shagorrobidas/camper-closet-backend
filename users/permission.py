from uuid import UUID
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from users.models import User


class ProfileAccessMixin:
    """
    Provides object-level permissions for user profiles.
    - If no `child` query-param (or pk kwarg) is provided,
      returns the authenticated user's profile.
    - If a child ID is provided (via ?child=<uuid> or
      URL kwarg pk), allows access when:
        1. The requested ID is the authenticated user.
        2. The authenticated user is a parent, and the
           requested ID belongs to their child.
    """
    def get_profile_user(self, follow_kwarg_pk=True):
        """
        Retrieves the user whose profile is being accessed.
        - Prioritizes ?child=<uuid> query parameter.
        - Optionally falls back to URL kwarg 'pk' if follow_kwarg_pk is True.
        - Defaults to authenticated user.
        """
        # 1. Try ?child= query param first as it's explicit for child access
        child_param = self.request.query_params.get('child')
        pk = None

        if child_param:
            try:
                pk = UUID(child_param)
            except (ValueError, AttributeError):
                raise ValidationError("Invalid child ID format.")

        # 2. Try URL kwarg if allowed and no child param provided
        if not pk and follow_kwarg_pk:
            pk = self.kwargs.get('pk')

        # Operate on self if no specific ID requested
        if not pk:
            return self.request.user

        user = get_object_or_404(User, pk=pk)

        # User accessing their own profile
        if user == self.request.user:
            return user

        # Parent accessing their child's profile
        if (
            self.request.user.role == 'parent'
            and user.parent == self.request.user
        ):
            return user

        raise PermissionDenied(
            "You do not have permission to access this profile."
        )
