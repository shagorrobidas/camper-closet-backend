from rest_framework.generics import ListAPIView
from closet.models import BrandCategoryType
from closet.api.serializers import BrandCategoryTypeSerializer
from core.utils import CustomResponse


class BrandCategoryTypeListView(ListAPIView):
    queryset = BrandCategoryType.objects.all()
    serializer_class = BrandCategoryTypeSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.queryset.all()
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            message="Brand category types retrieved successfully",
            status_code=200
        )