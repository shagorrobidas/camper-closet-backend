from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    RetrieveAPIView
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
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
        queryset = self.queryset.filter(user=user, is_active=True)

        # Filter by main_category
        main_category = request.query_params.get('main_category')
        if main_category:
            queryset = queryset.filter(main_category_id=main_category)

        # Filter by sub_category
        sub_category = request.query_params.get('sub_category')
        if sub_category:
            queryset = queryset.filter(sub_category_id=sub_category)

        # Filter favorites
        is_favorite = request.query_params.get('is_favorite')
        if is_favorite is not None:
            queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')

        # Search by name or brand
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(
                brand__icontains=search
            )

        # Sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        allowed_sorts = [
            'name', '-name', 'created_at', '-created_at', 'quantity', '-quantity'
        ]
        if sort_by in allowed_sorts:
            queryset = queryset.order_by(sort_by)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            message="Closet items retrieved successfully",
            status_code=200
        )


class ClosetItemDetailView(ProfileAccessMixin, RetrieveAPIView):
    queryset = ClosetItem.objects.all()
    serializer_class = ClosetItemSerializer

    def get(self, request, *args, **kwargs):
        try:
            item_pk = self.kwargs.get('pk')
            # ProfileAccessMixin's get_object() tries to find a User using `pk` from kwargs.
            # In this view, `pk` is the Item ID, so we must use request.user explicitly.
            user = request.user
            item = get_object_or_404(ClosetItem, pk=item_pk, user=user)
            serializer = self.get_serializer(item)
            return CustomResponse.success(
                data=serializer.data,
                message="Closet item retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class ClosetItemCreateView(ProfileAccessMixin, CreateAPIView):
    queryset = ClosetItem.objects.all()
    serializer_class = ClosetItemSerializer

    def create(self, request, *args, **kwargs):
        try:
            # We use request.user directly because get_object() in ProfileAccessMixin
            # expects a user pk in the URL, which is absent for item creation.
            user = request.user
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
            item_pk = self.kwargs.pop('pk', None)
            user = request.user
            item = get_object_or_404(ClosetItem, pk=item_pk)

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
            item_pk = self.kwargs.pop('pk', None)
            user = request.user
            item = get_object_or_404(ClosetItem, pk=item_pk)

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


class ClosetItemToggleFavoriteView(ProfileAccessMixin, APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        try:
            item_pk = self.kwargs.get('pk')
            user = request.user
            item = get_object_or_404(ClosetItem, pk=item_pk, user=user)
            item.is_favorite = not item.is_favorite
            item.save(update_fields=['is_favorite'])
            return CustomResponse.success(
                data={'is_favorite': item.is_favorite},
                message="Favorite status updated",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)
