from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from closet.models import ItemCategory
from closet.api.serializers import ItemCategorySerializer
from core.utils import CustomResponse
from django.db.models import Q


class ItemCategoryListCreateView(ListCreateAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        request_user = self.request.user
        target_user = serializer.validated_data.get('user', None)

        if not target_user:
            target_user = request_user
        elif target_user != request_user:
            if getattr(request_user, 'role', None) != 'parent':
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    "You can only create items for yourself."
                )
            if target_user.parent != request_user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    "You can only create items for your own children."
                )

        serializer.save(user=target_user)

    def get_queryset(self):
        user = self.request.user
        queryset = ItemCategory.objects.none()

        if getattr(user, 'role', None) == 'parent':
            queryset = ItemCategory.objects.filter(
                Q(user=user) | Q(user__parent=user)
            )
        else:
            queryset = ItemCategory.objects.filter(user=user)

        # Allow filtering by a specific child user ID (e.g., ?child=<id>)
        child_user_id = self.request.query_params.get('child')
        if child_user_id:
            queryset = queryset.filter(user_id=child_user_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="ItemCategory retrieved successfully",
            data=serializer.data,
        )
