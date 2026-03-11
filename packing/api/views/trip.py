import logging
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from packing.models import (
    Trip, PackingTemplate, TripPackingItem, PackingTemplateItem,
    TripPackingItemSelection, TripEvent
)
from closet.models import ClosetItem
from packing.api.serializers import (
    TripSerializer, TripDetailSerializer, TripPackingItemSerializer,
    TripPackingItemCreateSerializer
)
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler

logger = logging.getLogger(__name__)


def _create_trip_events(trip):
    """Auto-generate standard timeline events for a trip."""
    if trip.packing_deadline:
        TripEvent.objects.create(
            trip=trip,
            title='Packing Deadline',
            event_type='deadline',
            date=timezone.make_aware(
                timezone.datetime.combine(trip.packing_deadline, timezone.datetime.min.time())
            )
        )
    TripEvent.objects.create(
        trip=trip,
        title='Trip Starts',
        event_type='trip_start',
        date=timezone.make_aware(
            timezone.datetime.combine(trip.start_date, timezone.datetime.min.time())
        )
    )
    TripEvent.objects.create(
        trip=trip,
        title='Trip Ends',
        event_type='trip_end',
        date=timezone.make_aware(
            timezone.datetime.combine(trip.end_date, timezone.datetime.min.time())
        )
    )


class TripListView(ProfileAccessMixin, ListAPIView):
    serializer_class = TripSerializer

    def get(self, request, *args, **kwargs):
        user = self.get_profile_user()
        queryset = Trip.objects.filter(user=user).order_by('-created_at')

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data=serializer.data,
            message="Trips retrieved successfully",
            status_code=200
        )


class TripDetailView(ProfileAccessMixin, RetrieveAPIView):
    serializer_class = TripDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            user = self.get_profile_user()
            logger.info(f"trip_pk: {trip_pk}")
            logger.info(f"user: {user}")
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            logger.info(f"trip: {trip}")
            serializer = self.get_serializer(trip)
            return CustomResponse.success(
                data=serializer.data,
                message="Trip retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripCreateView(ProfileAccessMixin, CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def create(self, request, *args, **kwargs):
        user = self.get_profile_user()
        data = request.data.copy()
        data['user'] = user.id
        data['status'] = 'Active'

        template_id = data.get('template')
        template = None
        if template_id:
            try:
                template = PackingTemplate.objects.get(id=template_id)
                if template.trip_type:
                    data['trip_type'] = template.trip_type.id
            except (PackingTemplate.DoesNotExist, ValueError):
                pass

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            trip = serializer.save()

            # Auto-generate trip events
            _create_trip_events(trip)

            if template:
                template_items = PackingTemplateItem.objects.filter(
                    template=template
                ).order_by('sort_order')

                for t_item in template_items:
                    required_qty = t_item.quantity

                    p_item = TripPackingItem.objects.create(
                        trip=trip,
                        status='active',
                        main_category=t_item.main_category,
                        sub_category=t_item.sub_category,
                        title=t_item.title or (
                            t_item.sub_category.name if t_item.sub_category else ''
                        ),
                        template_item=t_item,
                        quantity=required_qty,
                        picked_quantity=0,
                        is_required=t_item.is_required,
                        is_packed=False,
                        is_custom_item=False,
                        note=t_item.note,
                        sort_order=t_item.sort_order
                    )

                    # Smart closet matching by sub_category
                    closet_items = ClosetItem.objects.filter(
                        user=user,
                        sub_category=t_item.sub_category,
                        is_active=True
                    ).order_by('-quantity')

                    remaining_qty = required_qty
                    picked_qty_total = 0

                    for c_item in closet_items:
                        if remaining_qty <= 0:
                            break
                        pick_qty = min(remaining_qty, c_item.quantity)
                        if pick_qty > 0:
                            TripPackingItemSelection.objects.create(
                                packing_item=p_item,
                                closet_item=c_item,
                                quantity=pick_qty
                            )
                            remaining_qty -= pick_qty
                            picked_qty_total += pick_qty

                    if picked_qty_total > 0:
                        p_item.picked_quantity = picked_qty_total
                        if picked_qty_total >= required_qty:
                            p_item.is_packed = True
                            p_item.packed_at = timezone.now()
                        p_item.save(
                            update_fields=['picked_quantity', 'is_packed', 'packed_at']
                        )

                trip.is_template_applied = True
                trip.save(update_fields=['is_template_applied'])

        detail_serializer = TripDetailSerializer(trip, context={'request': request})
        return CustomResponse.success(
            data=detail_serializer.data,
            message="Trip created successfully",
            status_code=201
        )


class TripUpdateView(ProfileAccessMixin, UpdateAPIView):
    serializer_class = TripSerializer

    def update(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.pop('pk', None)
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(trip, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Trip updated successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripDeleteView(ProfileAccessMixin, DestroyAPIView):

    def destroy(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.pop('pk', None)
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            trip.delete()
            return CustomResponse.success(
                message="Trip deleted successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


# ── Packing Items ───────────────────────────────────────────────────────────────

class TripPackingItemListView(ProfileAccessMixin, ListAPIView):
    serializer_class = TripPackingItemSerializer

    def get(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            queryset = trip.packing_items.filter(status='active').order_by('sort_order')

            main_category = request.query_params.get('main_category')
            if main_category:
                queryset = queryset.filter(main_category_id=main_category)

            sub_category = request.query_params.get('sub_category')
            if sub_category:
                queryset = queryset.filter(sub_category_id=sub_category)

            is_packed = request.query_params.get('is_packed')
            if is_packed is not None:
                queryset = queryset.filter(is_packed=is_packed.lower() == 'true')

            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(
                data=serializer.data,
                message="Packing items retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripPackingItemCreateView(ProfileAccessMixin, CreateAPIView):
    serializer_class = TripPackingItemCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            item = serializer.save(
                trip=trip,
                is_custom_item=True,
                status='active'
            )
            out = TripPackingItemSerializer(item, context={'request': request})
            return CustomResponse.success(
                data=out.data,
                message="Custom packing item added successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripPackingItemUpdateView(ProfileAccessMixin, UpdateAPIView):
    serializer_class = TripPackingItemSerializer

    def update(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            item_pk = self.kwargs.get('pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            item = get_object_or_404(TripPackingItem, pk=item_pk, trip=trip)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(item, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return CustomResponse.success(
                data=serializer.data,
                message="Packing item updated successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripPackingItemDeleteView(ProfileAccessMixin, DestroyAPIView):

    def destroy(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            item_pk = self.kwargs.get('pk')
            user = self.get_profile_user()
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            item = get_object_or_404(
                TripPackingItem, pk=item_pk, trip=trip, is_custom_item=True
            )
            item.delete()
            return CustomResponse.success(
                message="Custom item removed successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)