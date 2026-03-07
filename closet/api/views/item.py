from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from django.shortcuts import get_object_or_404
from closet.models import ClosetItem
from closet.api.serializers import ClosetItemSerializer
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler


class ClosetItemListView(ProfileAccessMixin, ListAPIView):
    queryset = ClosetItem.objects.all()
    serializer_class = ClosetItemSerializer

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        queryset = self.queryset.filter(user=user)

        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        brand_type = request.query_params.get('brand_type')
        if brand_type:
            queryset = queryset.filter(
                category__type_id=brand_type
            )

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            message="Closet items retrieved successfully",
            status_code=200
        )


class ClosetItemCreateView(ProfileAccessMixin, CreateAPIView):
    queryset = ClosetItem.objects.all()
    serializer_class = ClosetItemSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return CustomResponse.success(
                data=serializer.data,
                message="Closet item created successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class ClosetItemUpdateView(ProfileAccessMixin, UpdateAPIView):
    queryset = ClosetItem.objects.all()
    serializer_class = ClosetItemSerializer

    def update(self, request, *args, **kwargs):
        try:
            # Resolve user via ProfileAccessMixin (self or child)
            item_pk = self.kwargs.pop('pk', None)
            user = self.get_object()

            # Look up the ClosetItem by pk
            item = get_object_or_404(ClosetItem, pk=item_pk)

            # Check ownership: item must belong to resolved user
            if item.user != user:
                return CustomResponse.error(
                    message="You do not have permission to update this item.",
                    status_code=403
                )

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                item, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Closet item updated successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class ClosetItemDeleteView(ProfileAccessMixin, DestroyAPIView):
    queryset = ClosetItem.objects.all()
    serializer_class = ClosetItemSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            # Resolve user via ProfileAccessMixin (self or child)
            item_pk = self.kwargs.pop('pk', None)
            user = self.get_object()

            # Look up the ClosetItem by pk
            item = get_object_or_404(ClosetItem, pk=item_pk)

            # Check ownership: item must belong to resolved user
            if item.user != user:
                return CustomResponse.error(
                    message="You do not have permission to delete this item.",
                    status_code=403
                )

            item.delete()
            return CustomResponse.success(
                message="Closet item deleted successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

