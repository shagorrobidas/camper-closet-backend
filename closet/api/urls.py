from django.urls import path
from closet.api.views import (
    BrandCategoryTypeListView,
    ItemCategoryListView,
    ItemCategoryCreateView,
    ClosetItemListView,
    ClosetItemCreateView,
    ClosetItemUpdateView,
    ClosetItemDeleteView,
)

urlpatterns = [
    path(
        'brand-category-types/',
        BrandCategoryTypeListView.as_view(),
        name='brand_category_types'
    ),
    path(
        'item-categories/',
        ItemCategoryListView.as_view(),
        name='item_categories'
    ),
    path(
        'item-categories/create/',
        ItemCategoryCreateView.as_view(),
        name='item_categories_create'
    ),
    path(
        'items/',
        ClosetItemListView.as_view(),
        name='closet_items'
    ),
    path(
        'items/create/',
        ClosetItemCreateView.as_view(),
        name='closet_items_create'
    ),
    path(
        'items/update/<uuid:pk>/',
        ClosetItemUpdateView.as_view(),
        name='closet_items_update'
    ),
    path(
        'items/delete/<uuid:pk>/',
        ClosetItemDeleteView.as_view(),
        name='closet_items_delete'
    ),
]
