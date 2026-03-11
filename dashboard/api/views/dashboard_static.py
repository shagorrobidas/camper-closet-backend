from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from closet.models import ClosetItem, ItemCategoryType
from users.permission import ProfileAccessMixin
from core.utils import CustomResponse, custom_exception_handler


class DashboardStatsView(ProfileAccessMixin, GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_profile_user()

            total_items = ClosetItem.objects.filter(
                user=user
            ).count()

            brand_types = ItemCategoryType.objects.annotate(
                item_count=Count(
                    'closet_items_main',
                    filter=Q(closet_items_main__user=user)
                )
            ).values(
                'id',
                'name',
                'code',
                'item_count'
            )

            data = {
                'total_items': total_items,
                'brand_category_stats': list(brand_types),
            }

            return CustomResponse.success(
                data=data,
                message="Dashboard stats retrieved successfully",
                status_code=200,
            )

        except Exception as e:
            return custom_exception_handler(e, request)