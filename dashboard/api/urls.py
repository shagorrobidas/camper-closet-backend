from django.urls import path
from dashboard.api.views import (
    DashboardStatsView,
    ShopWebsiteListView
)

urlpatterns = [
    path(
        'statics/',
        DashboardStatsView.as_view(),
        name='dashboard_stats'
    ),
    path(
        'shop-websites/',
        ShopWebsiteListView.as_view(),
        name='shop_websites'
    ),
]