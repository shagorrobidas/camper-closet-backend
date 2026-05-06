from rest_framework.generics import CreateAPIView
from packing.models import PackingTemplate
from packing.api.serializers.create_template import PackingTemplateCreateSerializer
from core.utils import CustomResponse


class PackingTemplateCreateAPIView(CreateAPIView):
    queryset = PackingTemplate.objects.all()
    serializer_class = PackingTemplateCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return CustomResponse.success(
            data=serializer.data,
            message="Packing template and items created successfully",
            status_code=201
        )
