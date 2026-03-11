from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from users.models import Notification, NotificationSetting
from users.api.serializers import (
    NotificationSerializer, NotificationSettingSerializer
)
from core.utils import CustomResponse, custom_exception_handler


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')

            is_read = request.query_params.get('is_read')
            if is_read is not None:
                notifications = notifications.filter(
                    is_read=is_read.lower() == 'true'
                )

            paginator = NotificationPagination()
            page = paginator.paginate_queryset(notifications, request)
            serializer = NotificationSerializer(page, many=True)
            return CustomResponse.success(
                data={
                    'notifications': serializer.data,
                    'count': paginator.page.paginator.count,
                    'unread_count': Notification.objects.filter(
                        user=request.user, is_read=False
                    ).count(),
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                },
                message="Notifications retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """Mark a single notification or all as read."""
        try:
            notification_pk = self.kwargs.get('pk')
            if notification_pk:
                notification = get_object_or_404(
                    Notification, pk=notification_pk, user=request.user
                )
                notification.is_read = True
                notification.save(update_fields=['is_read'])
            else:
                Notification.objects.filter(
                    user=request.user, is_read=False
                ).update(is_read=True)
            return CustomResponse.success(
                message="Marked as read",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class NotificationSettingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        setting, _ = NotificationSetting.objects.get_or_create(user=request.user)
        serializer = NotificationSettingSerializer(setting)
        return CustomResponse.success(
            data=serializer.data,
            message="Notification settings retrieved",
            status_code=200
        )

    def patch(self, request, *args, **kwargs):
        try:
            setting, _ = NotificationSetting.objects.get_or_create(user=request.user)
            serializer = NotificationSettingSerializer(
                setting, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Notification settings updated",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)
