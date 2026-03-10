from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from packing.models import (
    Trip, TripPackingItem, TripPackingItemSelection, TripEvent
)
from closet.models import ClosetItem
from packing.api.serializers import (
    TripPackingItemSelectionSerializer, TripEventSerializer
)
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler


def _refresh_packing_item_status(packing_item):
    """Recalculate picked_quantity and packed status from selections."""
    total_picked = sum(
        s.quantity for s in packing_item.selections.all()
    )
    packing_item.picked_quantity = total_picked
    if total_picked >= packing_item.quantity:
        packing_item.is_packed = True
        if not packing_item.packed_at:
            packing_item.packed_at = timezone.now()
    else:
        packing_item.is_packed = False
        packing_item.packed_at = None
    packing_item.save(
        update_fields=['picked_quantity', 'is_packed', 'packed_at']
    )


class PackingItemSelectClosetView(ProfileAccessMixin, APIView):
    """POST to add a closet item selection to a packing item."""

    def post(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            item_pk = self.kwargs.get('item_pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            packing_item = get_object_or_404(TripPackingItem, pk=item_pk, trip=trip)

            closet_item_id = request.data.get('closet_item')
            quantity = int(request.data.get('quantity', 1))
            note = request.data.get('note', '')

            closet_item = get_object_or_404(ClosetItem, pk=closet_item_id)

            # Enforce same-user ownership for the closet item
            if closet_item.user != user:
                raise PermissionDenied(
                    "This closet item does not belong to you."
                )

            if quantity < 1:
                raise ValidationError("Quantity must be at least 1.")

            # Prevent duplicate selection of the same closet item
            selection, created = TripPackingItemSelection.objects.get_or_create(
                packing_item=packing_item,
                closet_item=closet_item,
                defaults={'quantity': quantity, 'note': note}
            )
            if not created:
                selection.quantity = quantity
                selection.note = note
                selection.save(update_fields=['quantity', 'note'])

            _refresh_packing_item_status(packing_item)

            serializer = TripPackingItemSelectionSerializer(
                selection, context={'request': request}
            )
            return CustomResponse.success(
                data=serializer.data,
                message="Closet item selected successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class PackingItemRemoveClosetView(ProfileAccessMixin, APIView):
    """DELETE to remove a closet item selection from a packing item."""

    def delete(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            item_pk = self.kwargs.get('item_pk')
            selection_pk = self.kwargs.get('selection_pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            packing_item = get_object_or_404(TripPackingItem, pk=item_pk, trip=trip)
            selection = get_object_or_404(
                TripPackingItemSelection, pk=selection_pk, packing_item=packing_item
            )
            selection.delete()
            _refresh_packing_item_status(packing_item)
            return CustomResponse.success(
                message="Selection removed successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class ClosetMatchSuggestionView(ProfileAccessMixin, APIView):
    """GET smart closet item suggestions for a packing item based on sub_category."""

    def get(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            item_pk = self.kwargs.get('item_pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            packing_item = get_object_or_404(TripPackingItem, pk=item_pk, trip=trip)

            already_selected_ids = packing_item.selections.values_list(
                'closet_item_id', flat=True
            )

            suggestions = ClosetItem.objects.filter(
                user=user,
                sub_category=packing_item.sub_category,
                is_active=True
            ).exclude(id__in=already_selected_ids).order_by('-quantity')

            from closet.api.serializers import ClosetItemSerializer
            serializer = ClosetItemSerializer(
                suggestions, many=True, context={'request': request}
            )
            return CustomResponse.success(
                data=serializer.data,
                message="Suggestions retrieved",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


# ── Trip Events ─────────────────────────────────────────────────────────────────

class TripEventListView(ProfileAccessMixin, ListAPIView):
    serializer_class = TripEventSerializer

    def get(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            events = trip.events.all().order_by('date')
            serializer = self.get_serializer(events, many=True)
            return CustomResponse.success(
                data=serializer.data,
                message="Trip events retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripEventCreateView(ProfileAccessMixin, CreateAPIView):
    serializer_class = TripEventSerializer

    def create(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            event = serializer.save(trip=trip)
            return CustomResponse.success(
                data=TripEventSerializer(event).data,
                message="Event created successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripEventDeleteView(ProfileAccessMixin, DestroyAPIView):

    def destroy(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            event_pk = self.kwargs.get('pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            event = get_object_or_404(
                TripEvent, pk=event_pk, trip=trip, event_type='custom'
            )
            event.delete()
            return CustomResponse.success(
                message="Event deleted successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)
