from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from closet.models import ClosetItem
from closet.api.serializers import ClosetItemSerializer
from core.utils import CustomResponse


class ClosetItemListView(ListCreateAPIView):
    queryset = ClosetItem.objects.all()
    serializer_class = ClosetItemSerializer
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
        queryset = ClosetItem.objects.none()

        if getattr(user, 'role', None) == 'parent':
            from django.db.models import Q
            queryset = ClosetItem.objects.filter(
                Q(user=user) | Q(user__parent=user)
            )
            # Allow filtering by a specific child user ID (e.g., ?child=<id>)
            child_user_id = self.request.query_params.get('child')
            if child_user_id:
                queryset = queryset.filter(user_id=child_user_id)
        else:
            queryset = ClosetItem.objects.filter(user=user)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="ClosetItem retrieved successfully",
            data=serializer.data,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return CustomResponse.success(
            message="ClosetItem created successfully",
            data=serializer.data,
            status_code=201,
        )

# End of file

