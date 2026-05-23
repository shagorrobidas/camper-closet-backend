from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAuthenticated
from packing.models import PackingTemplateCategory
from packing.api.serializers import PackingTemplateCategorySerializer
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler


class PackingTemplateCategoryListView(ProfileAccessMixin, ListCreateAPIView):
    queryset = PackingTemplateCategory.objects.all().order_by('sort_order', 'created_at')
    serializer_class = PackingTemplateCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        template_id = self.request.query_params.get('template')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(
                data=serializer.data,
                message="Template categories retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Template category created successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class PackingTemplateCategoryDetailView(ProfileAccessMixin, RetrieveUpdateDestroyAPIView):
    queryset = PackingTemplateCategory.objects.all()
    serializer_class = PackingTemplateCategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse.success(
                data=serializer.data,
                message="Template category retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Template category updated successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def put(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Template category updated successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return CustomResponse.success(
                message="Template category deleted successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)
