from django.urls import path
from closet.api.views import (
    ItemCategoryListCreateView,
    ClosetItemListView
)

urlpatterns = [
    path(
        'item-category/',
        ItemCategoryListCreateView.as_view(),
        name='item-category-list-create'
    ),
    path(
        'items/',
        ClosetItemListView.as_view(),
        name='items-list-create'
    )
]