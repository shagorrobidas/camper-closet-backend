from rest_framework.generics import ListAPIView, CreateAPIView
from closet.models import ItemCategory
from closet.api.serializers import ItemCategorySerializer
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler
from django.db.models import Q


class ItemCategoryListView(ProfileAccessMixin, ListAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        # Return system categories + this user's custom categories
        queryset = ItemCategory.objects.filter(
            Q(is_system=True) | Q(user=user)
        ).select_related('type')

        type_id = request.query_params.get('type')
        if type_id:
            queryset = queryset.filter(type_id=type_id)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            message="Item categories retrieved successfully",
            status_code=200
        )


class ItemCategoryCreateView(ProfileAccessMixin, CreateAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer

    def create(self, request, *args, **kwargs):
        try:
            # We use request.user directly because get_object() expects a user pk
            user = request.user
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, is_custom=True, is_system=False)
            return CustomResponse.success(
                data=serializer.data,
                message="Item category created successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)
