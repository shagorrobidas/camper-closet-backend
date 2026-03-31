from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from dashboard.models import ShopWebsite
from core.utils import CustomResponse, custom_exception_handler
from dashboard.api.serializers import ShopWebsiteSerializer


class ShopWebsiteListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopWebsiteSerializer
    queryset = ShopWebsite.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            return CustomResponse.success(
                message="Shop websites fetched successfully",
                data=response.data
            )
        except Exception as e:
            return custom_exception_handler(e, None)
