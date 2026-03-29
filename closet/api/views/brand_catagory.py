from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from closet.models import ItemCategoryType
from closet.api.serializers import ItemCategoryTypeSerializer
from core.utils import CustomResponse


class ItemCategoryTypeListView(ListAPIView):
    queryset = ItemCategoryType.objects.all()
    serializer_class = ItemCategoryTypeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.queryset.all()
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            message="Brand category types retrieved successfully",
            status_code=200
        )
