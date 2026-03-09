from rest_framework.generics import CreateAPIView
from django.db import transaction
from packing.models import (
    Trip,
    PackingTemplate, PackingList, PackingListItem, PackingTemplateItem
)
from closet.models import ClosetItem
from packing.api.serializers import TripSerializer
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse


class TripCreateView(ProfileAccessMixin, CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def create(self, request, *args, **kwargs):
        user = self.get_object()
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

            if template:
                # 1. Create PackingList
                packing_list = PackingList.objects.create(
                    trip=trip,
                    title=f"Packing List for {trip.name}",
                    status='active'
                )

                # 2. Get Template Items
                template_items = PackingTemplateItem.objects.filter(
                    template=template
                )

                # 3. Process each template item to auto-populate PackingList
                for t_item in template_items:
                    required_qty = t_item.quantity

                    # Find user's closet items for this sub_category
                    closet_items = ClosetItem.objects.filter(
                        user=user,
                        category=t_item.sub_category
                    ).order_by('-quantity')

                    remaining_qty = required_qty

                    # Proportionally allocate from closet items
                    for c_item in closet_items:
                        if remaining_qty <= 0:
                            break

                        # How much can we take from this closet item?
                        pick_qty = min(remaining_qty, c_item.quantity)

                        if pick_qty > 0:
                            PackingListItem.objects.create(
                                packing_list=packing_list,
                                template_item=t_item,
                                closet_item=c_item,
                                category=t_item.sub_category,
                                quantity=pick_qty,
                                picked_quantity=0,
                                is_packed=False,
                                is_custom_item=False,
                                note=t_item.note
                            )
                            remaining_qty -= pick_qty

                    # If some quantity is still required but no closet items found,
                    # create a placeholder item for the remaining quantity
                    if remaining_qty > 0:
                        PackingListItem.objects.create(
                            packing_list=packing_list,
                            template_item=t_item,
                            closet_item=None,
                            category=t_item.sub_category,
                            quantity=remaining_qty,
                            picked_quantity=0,
                            is_packed=False,
                            is_custom_item=False,
                            note=f"Required: {t_item.note or ''}"
                        )

        return CustomResponse.success(
            data=serializer.data,
            message="Trip and automated packing list created successfully",
            status_code=201
        )