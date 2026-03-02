from rest_framework.generics import ListAPIView
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
        return CustomResponse(
            data=serializer.data,
            message="Item categories retrieved successfully",
            status_code=200
        )
