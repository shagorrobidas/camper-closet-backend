from rest_framework.generics import ListAPIView, CreateAPIView
from closet.models import ItemCategory
from closet.api.serializers import ItemCategorySerializer
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse


class ItemCategoryListView(ProfileAccessMixin, ListAPIView):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        queryset = self.queryset.filter(user=user)
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
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return CustomResponse.success(
            data=serializer.data,
            message="Item category created successfully",
            status_code=201
        )
