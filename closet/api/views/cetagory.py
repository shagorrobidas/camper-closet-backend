from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from closet.models import ItemCategoryType, ItemCategory
from closet.api.serializers.cetagory import (
    ClosetCategorySerializer,
    ClosetCategoryDetailSerializer,
    ClosetSubCategorySerializer,
)
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler


class ClosetCategoryApiView(ProfileAccessMixin, APIView):
    serializer_class = ClosetCategorySerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': getattr(self, 'format_kwarg', None),
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            serializer_class = ClosetCategoryDetailSerializer
        else:
            serializer_class = ClosetCategorySerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get(self, request, pk=None, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            category_id = pk or request.query_params.get('pk') or request.query_params.get('id')

            if category_id:
                # Retrieve specific category details
                category = get_object_or_404(
                    ItemCategoryType,
                    Q(pk=category_id) & (Q(user__isnull=True) | Q(user=user))
                )
                serializer = self.get_serializer(category, context={'user': user})
                return CustomResponse.success(
                    data=serializer.data,
                    message="Category retrieved successfully",
                    status_code=200
                )

            # List categories strictly belonging to the logged-in user
            queryset = ItemCategoryType.objects.filter(
                user=user
            ).order_by('-created_at')

            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(name__icontains=search)

            serializer = self.get_serializer(queryset, many=True, context={'user': user})
            return CustomResponse.success(
                data=serializer.data,
                message="Categories retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def post(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return CustomResponse.success(
                data=serializer.data,
                message="Category created successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def patch(self, request, pk=None, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            category_id = pk or request.data.get('id') or request.data.get('pk') or request.query_params.get('pk') or request.query_params.get('id')
            if not category_id:
                return CustomResponse.error(
                    message="Category ID is required for update.",
                    status_code=400
                )

            category = get_object_or_404(ItemCategoryType, pk=category_id, user=user)
            serializer = self.get_serializer(category, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Category updated successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            category_id = pk or request.query_params.get('pk') or request.query_params.get('id') or request.data.get('id') or request.data.get('pk')
            if not category_id:
                return CustomResponse.error(
                    message="Category ID is required for deletion.",
                    status_code=400
                )

            category = get_object_or_404(ItemCategoryType, pk=category_id, user=user)
            category.delete()
            return CustomResponse.success(
                message="Category deleted successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class ClosetSubCategoryApiView(ProfileAccessMixin, APIView):
    serializer_class = ClosetSubCategorySerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': getattr(self, 'format_kwarg', None),
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return ClosetSubCategorySerializer(*args, **kwargs)

    def get(self, request, pk=None, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            subcategory_id = pk or request.query_params.get('pk') or request.query_params.get('id')

            if subcategory_id:
                # Retrieve specific subcategory details
                subcategory = get_object_or_404(
                    ItemCategory,
                    Q(pk=subcategory_id) & (Q(is_system=True) | Q(user=user))
                )
                serializer = self.get_serializer(subcategory)
                return CustomResponse.success(
                    data=serializer.data,
                    message="Sub-category retrieved successfully",
                    status_code=200
                )

            # List subcategories belonging to the logged-in user or the user's custom categories
            queryset = ItemCategory.objects.filter(
                Q(user=user) | Q(type__user=user)
            ).select_related('type').order_by('-created_at')

            type_param = request.query_params.get('type')
            if type_param:
                queryset = queryset.filter(type_id=type_param)

            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(name__icontains=search)

            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(
                data=serializer.data,
                message="Sub-categories retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def post(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, is_custom=True, is_system=False)
            return CustomResponse.success(
                data=serializer.data,
                message="Sub-category created successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def patch(self, request, pk=None, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            subcategory_id = pk or request.data.get('id') or request.data.get('pk') or request.query_params.get('pk') or request.query_params.get('id')
            if not subcategory_id:
                return CustomResponse.error(
                    message="Sub-category ID is required for update.",
                    status_code=400
                )

            subcategory = get_object_or_404(ItemCategory, pk=subcategory_id, user=user)
            serializer = self.get_serializer(subcategory, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Sub-category updated successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            subcategory_id = pk or request.query_params.get('pk') or request.query_params.get('id') or request.data.get('id') or request.data.get('pk')
            if not subcategory_id:
                return CustomResponse.error(
                    message="Sub-category ID is required for deletion.",
                    status_code=400
                )

            subcategory = get_object_or_404(ItemCategory, pk=subcategory_id, user=user)
            subcategory.delete()
            return CustomResponse.success(
                message="Sub-category deleted successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)
