from rest_framework.generics import ListAPIView, RetrieveAPIView
from packing.models import PackingTemplate
from packing.api.serializers import (
    PackingTemplateSerializer,
    PackingTemplateDetailSerializer
)
from core.utils import CustomResponse


class PackingTemplateListView(ListAPIView):
    queryset = PackingTemplate.objects.all()
    serializer_class = PackingTemplateSerializer

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_system=True)
        trip_type = self.request.query_params.get('trip_type')
        season = self.request.query_params.get('season')

        if trip_type:
            queryset = queryset.filter(trip_type_id=trip_type)
        if season:
            queryset = queryset.filter(season=season)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            message="Packing templates retrieved successfully",
            status_code=200
        )


class PackingTemplateDetailView(RetrieveAPIView):
    queryset = PackingTemplate.objects.all()
    serializer_class = PackingTemplateDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse.success(
                data=serializer.data,
                message="Packing template retrieved successfully",
                status_code=200
            )
        except PackingTemplate.DoesNotExist:
            return CustomResponse.error(
                data=None,
                message="Packing template not found",
                status_code=404
            )
