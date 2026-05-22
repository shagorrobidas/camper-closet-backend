import logging
from rest_framework.permissions import IsAuthenticated
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
    Trip,
    PackingTemplate,
    TripPackingItem,
    PackingTemplateItem,
    TripEvent,
    TripType
)
from closet.models import (
    ItemCategoryType
)
from packing.api.serializers import (
    TripSerializer, TripDetailSerializer, TripPackingItemSerializer,
    TripPackingItemCreateSerializer,
    TripTypeSerializer,
    ActiveIncompleteTripPackingItemSerializer,
    TripStatisticsSerializer,
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
                timezone.datetime.combine(
                    trip.packing_deadline,
                    timezone.datetime.min.time()
                )
            )
        )
    TripEvent.objects.create(
        trip=trip,
        title='Trip Starts',
        event_type='trip_start',
        date=timezone.make_aware(
            timezone.datetime.combine(
                trip.start_date,
                timezone.datetime.min.time()
            )
        )
    )
    TripEvent.objects.create(
        trip=trip,
        title='Trip Ends',
        event_type='trip_end',
        date=timezone.make_aware(
            timezone.datetime.combine(
                trip.end_date,
                timezone.datetime.min.time()
            )
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
        stats_serializer = TripStatisticsSerializer(user)

        return CustomResponse.success(
            data={
                "statistics": stats_serializer.data,
                "trips": serializer.data
            },
            message="Trips retrieved successfully",
            status_code=200
        )


class TripDetailView(ProfileAccessMixin, RetrieveAPIView):
    serializer_class = TripDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('pk')
            user = self.get_profile_user(follow_kwarg_pk=False)
            logger.info(f"trip_pk: {trip_pk}")
            logger.info(f"user: {user}")
            trip = get_object_or_404(
                Trip.objects.select_related('template', 'trip_type').prefetch_related(
                    'template__categories',
                    'packing_items__template_item__category',
                    'packing_items__selections__closet_item'
                ),
                pk=trip_pk,
                user=user
            )
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
                return CustomResponse.error(
                    message="Template not found",
                    status_code=404
                )

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

                    TripPackingItem.objects.create(
                        trip=trip,
                        status='active',
                        title=t_item.title or '',
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
                #     closet_items = ClosetItem.objects.filter(
                #         user=user,
                #         sub_category=t_item.sub_category,
                #         is_active=True
                #     ).order_by('-quantity')

                #     remaining_qty = required_qty
                #     picked_qty_total = 0

                #     for c_item in closet_items:
                #         if remaining_qty <= 0:
                #             break
                #         pick_qty = min(remaining_qty, c_item.quantity)
                #         if pick_qty > 0:
                #             TripPackingItemSelection.objects.create(
                #                 packing_item=p_item,
                #                 closet_item=c_item,
                #                 quantity=pick_qty
                #             )
                #             remaining_qty -= pick_qty
                #             picked_qty_total += pick_qty

                #     if picked_qty_total > 0:
                #         p_item.picked_quantity = picked_qty_total
                #         if picked_qty_total >= required_qty:
                #             p_item.is_packed = True
                #             p_item.packed_at = timezone.now()
                #         p_item.save(
                #             update_fields=[
                #                 'picked_quantity',
                #                 'is_packed',
                #                 'packed_at'
                #             ]
                #         )

                trip.is_template_applied = True
                trip.save(update_fields=['is_template_applied'])

        detail_serializer = TripDetailSerializer(
            trip,
            context={'request': request}
        )
        return CustomResponse.success(
            data=detail_serializer.data,
            message="Trip created successfully",
            status_code=201
        )


class TripUpdateView(ProfileAccessMixin, UpdateAPIView):
    serializer_class = TripSerializer

    def update(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('pk')
            user = self.get_profile_user(follow_kwarg_pk=False)
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                trip,
                data=request.data,
                partial=partial
            )
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
            trip_pk = self.kwargs.get('pk')
            user = self.get_profile_user(follow_kwarg_pk=False)
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            trip.delete()
            return CustomResponse.success(
                message="Trip deleted successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripPackingItemListView(ProfileAccessMixin, ListAPIView):
    serializer_class = TripPackingItemSerializer

    def get(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            user = self.get_profile_user(follow_kwarg_pk=False)
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            queryset = trip.packing_items.filter(
                status='active'
            ).order_by('sort_order')

            main_category = request.query_params.get('main_category')
            if main_category:
                queryset = queryset.filter(main_category_id=main_category)

            sub_category = request.query_params.get('sub_category')
            if sub_category:
                queryset = queryset.filter(sub_category_id=sub_category)

            is_packed = request.query_params.get('is_packed')
            if is_packed is not None:
                queryset = queryset.filter(
                    is_packed=is_packed.lower() == 'true'
                )

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
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            user = self.get_profile_user(follow_kwarg_pk=False)
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                item = serializer.save(
                    trip=trip,
                    is_custom_item=True,
                    status='active'
                )
                
                # If trip has a non-system template, add this item to the template too
                if trip.template and not trip.template.is_system:
                    t_item = PackingTemplateItem.objects.create(
                        template=trip.template,
                        category=item.category,
                        title=item.title,
                        quantity=item.quantity,
                        is_required=item.is_required,
                        note=item.note,
                        sort_order=item.sort_order
                    )
                    item.template_item = t_item
                    item.save(update_fields=['template_item'])

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
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            trip_pk = self.kwargs.get('trip_pk')
            item_pk = self.kwargs.get('packing_item_pk')
            user = self.get_profile_user(follow_kwarg_pk=False)
            trip = get_object_or_404(Trip, pk=trip_pk, user=user)
            item = get_object_or_404(TripPackingItem, pk=item_pk, trip=trip)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                item,
                data=request.data,
                partial=partial
            )
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
            user = self.get_profile_user(follow_kwarg_pk=False)
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


class MenualTripCreateView(ProfileAccessMixin, CreateAPIView):
    serializer_class = TripSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            data = request.data.copy()
            data['user'] = user.id

            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                print("Serializer errors in MenualTripCreateView:")
                print(serializer.errors)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                trip_type_id = data.get('trip_type')
                trip_type = TripType.objects.get(id=trip_type_id)

                # 1. Create PackingTemplate first
                template = PackingTemplate.objects.create(
                    title=data.get('name'),
                    trip_type=trip_type,
                    season='None',
                    is_system=False
                )

                # 2. Create Trip
                trip = serializer.save(
                    user=user,
                    is_template_applied=False,
                    status='active',
                    trip_type=trip_type,
                    template=template
                )

                # Auto-generate trip events
                _create_trip_events(trip)

                # 3. Create PackingTemplateItems
                cat_types = ItemCategoryType.objects.all()
                for cat_type in cat_types:
                    PackingTemplateItem.objects.create(
                        template=template,
                        title=trip.name,
                        is_required=False,
                        quantity=0
                    )

                    # 4. Create TripPackingItems
                    TripPackingItem.objects.create(
                        trip=trip,
                        main_category=cat_type,
                        title=trip.name,
                        status='active',
                        is_required=False,
                        is_packed=False,
                        is_custom_item=False
                    )

            out = TripDetailSerializer(trip, context={'request': request})
            return CustomResponse.success(
                data=out.data,
                message="Trip created successfully",
                status_code=201
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class TripTypeListView(ProfileAccessMixin, ListAPIView):
    serializer_class = TripTypeSerializer

    def get(self, request, *args, **kwargs):
        try:
            queryset = TripType.objects.all()
            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(
                data=serializer.data,
                message="Trip types retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)


class ActiveIncompleteTripPackingItemListView(ProfileAccessMixin, ListAPIView):
    """
    Returns upcoming active trips (start_date >= today) that have at least
    one incomplete (is_packed=False) active packing item, grouped by trip.
    """
    serializer_class = ActiveIncompleteTripPackingItemSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user(follow_kwarg_pk=False)
            today = timezone.now().date()

            # Upcoming active trips that still have incomplete items
            queryset = Trip.objects.filter(
                user=user,
                start_date__gte=today,
                status='active',
                packing_items__status='active',
                packing_items__is_packed=False,
            ).distinct().prefetch_related(
                'packing_items'
            ).select_related(
                'trip_type'
            ).order_by('start_date')

            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(
                data=serializer.data,
                message="Incomplete packing items retrieved successfully",
                status_code=200
            )
        except Exception as e:
            return custom_exception_handler(e, request)
