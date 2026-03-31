from django.urls import path
from packing.api.views import (
    PackingTemplateListView,
    PackingTemplateDetailView,
    TripListView,
    TripDetailView,
    TripCreateView,
    TripUpdateView,
    TripDeleteView,
    TripPackingItemListView,
    TripPackingItemCreateView,
    TripPackingItemDeleteView,
    PackingItemSelectClosetView,
    PackingItemRemoveClosetView,
    ClosetMatchSuggestionView,
    TripBulkPackingView,
    TripEventListView,
    TripEventCreateView,
    TripEventDeleteView,
    TripPackingItemUpdateView,
    UpcomingTripEventListView,
    MenualTripCreateView,
    TripTypeListView,
    ActiveIncompleteTripPackingItemListView,
)

urlpatterns = [
    # Templates
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

    # Trips
    path(
        'trips/',
        TripListView.as_view(),
        name='trip-list'
    ),
    path(
        'trips/create/',
        TripCreateView.as_view(),
        name='trip-create'
    ),
    path(
        'trips/<uuid:pk>/',
        TripDetailView.as_view(),
        name='trip-detail'
    ),
    path(
        'trips/<uuid:pk>/update/',
        TripUpdateView.as_view(),
        name='trip-update'
    ),
    path(
        'trips/<uuid:pk>/delete/',
        TripDeleteView.as_view(),
        name='trip-delete'
    ),
    path(
        'trips/<uuid:trip_pk>/bulk-select-closet/',
        TripBulkPackingView.as_view(),
        name='trip-bulk-select-closet'
    ),

    # Trip Packing Items
    path(
        'trips/<uuid:trip_pk>/packing-items/',
        TripPackingItemListView.as_view(),
        name='trip-packing-item-list'
    ),
    path(
        'trips/<uuid:trip_pk>/packing-items/create/',
        TripPackingItemCreateView.as_view(),
        name='trip-packing-item-create'
    ),
    path(
        'trips/<uuid:trip_pk>/packing-items/<uuid:packing_item_pk>/update/',
        TripPackingItemUpdateView.as_view(),
        name='trip-packing-item-update'
    ),
    path(
        'trips/<uuid:trip_pk>/packing-items/<uuid:pk>/delete/',
        TripPackingItemDeleteView.as_view(),
        name='trip-packing-item-delete'
    ),

    path(
        'trips/menual-create/',
        MenualTripCreateView.as_view(),
        name='menual-trip-create'
    ),
    path(
        'trips/types/',
        TripTypeListView.as_view(),
        name='trip-type-list'
    ),
    path(
        'trips/incomplete-packing-items/',
        ActiveIncompleteTripPackingItemListView.as_view(),
        name='trips-incomplete-packing-items'
    ),

    # Closet Selection / Matching
    path(
        'trips/<uuid:trip_pk>/packing-items/<uuid:item_pk>/select-closet/',
        PackingItemSelectClosetView.as_view(),
        name='packing-item-select-closet'
    ),
    path(
        'trips/<uuid:trip_pk>/packing-items/<uuid:item_pk>/suggest-closet/',
        ClosetMatchSuggestionView.as_view(),
        name='packing-item-suggest-closet'
    ),
    path(
        'trips/<uuid:trip_pk>/packing-items/<uuid:item_pk>/selections/<uuid:selection_pk>/remove/', # noqa
        PackingItemRemoveClosetView.as_view(),
        name='packing-item-remove-selection'
    ),

    # Trip Events / Calendar
    path(
        'trips/<uuid:trip_pk>/events/',
        TripEventListView.as_view(),
        name='trip-event-list'
    ),
    path(
        'trips/<uuid:trip_pk>/events/create/',
        TripEventCreateView.as_view(),
        name='trip-event-create'
    ),
    path(
        'trips/<uuid:trip_pk>/events/<uuid:pk>/delete/',
        TripEventDeleteView.as_view(),
        name='trip-event-delete'
    ),

    # Upcoming Events (Global)
    path(
        'trips/upcoming-events/',
        UpcomingTripEventListView.as_view(),
        name='upcoming-trip-events'
    ),
]
