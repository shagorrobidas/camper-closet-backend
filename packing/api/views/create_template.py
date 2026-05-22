from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from packing.models import PackingTemplate
from packing.api.serializers import PackingTemplateCreateSerializer
from core.utils import CustomResponse


class PackingTemplateCreateAPIView(CreateAPIView):
    queryset = PackingTemplate.objects.all()
    serializer_class = PackingTemplateCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return CustomResponse.success(
            data=serializer.data,
            message="Packing template and items created successfully",
            status_code=201
        )
