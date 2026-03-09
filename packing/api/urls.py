from django.urls import path
from packing.api.views import (
    PackingTemplateListView,
    PackingTemplateDetailView,
    TripCreateView
)


urlpatterns = [
    path(
        'templates/',
        PackingTemplateListView.as_view(),
        name='packing-template-list'
    ),
    path(
        'templates/<uuid:pk>/',
        PackingTemplateDetailView.as_view(),
        name='packing-template-detail'
    ),
    path(
        'trips/create/',
        TripCreateView.as_view(),
        name='trip-create'
    ),
]