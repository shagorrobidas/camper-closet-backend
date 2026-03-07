from django.urls import path
from dashboard.api.views import DashboardStatsView

urlpatterns = [
    path(
        'closet/statics/',
        DashboardStatsView.as_view(),
        name='dashboard_stats'
    ),
]