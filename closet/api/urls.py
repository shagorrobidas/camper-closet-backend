from django.urls import path
from closet.api.views import (
    ItemCategoryTypeListView,
    ItemCategoryListView,
    ItemCategoryCreateView,
    ClosetItemListView,
    ClosetItemDetailView,
    ClosetItemCreateView,
    ClosetItemUpdateView,
    ClosetItemDeleteView,
    ClosetItemToggleFavoriteView,
    ScanItemView,
    ClosetCategoryApiView,
    ClosetSubCategoryApiView,
)

urlpatterns = [
    path(
        'category-types/',
        ItemCategoryTypeListView.as_view(),
        name='category_types'
    ),
    path(
        'categories/',
        ItemCategoryListView.as_view(),
        name='item_categories'
    ),
    path(
        'categories/create/',
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
        'items/<uuid:item_pk>/',
        ClosetItemDetailView.as_view(),
        name='closet_items_detail'
    ),
    path(
        'items/<uuid:item_pk>/update/',
        ClosetItemUpdateView.as_view(),
        name='closet_items_update'
    ),
    path(
        'items/<uuid:item_pk>/delete/',
        ClosetItemDeleteView.as_view(),
        name='closet_items_delete'
    ),
    path(
        'items/<uuid:item_pk>/toggle-favorite/',
        ClosetItemToggleFavoriteView.as_view(),
        name='closet_items_toggle_favorite'
    ),
    path(
        'items/scan/',
        ScanItemView.as_view(),
        name='closet_items_scan'
    ),

    # Main category APIs (ItemCategoryType)
    path(
        'closet-category/',
        ClosetCategoryApiView.as_view(),
        name='closet_category_list_create'
    ),
    path(
        'closet-category/<uuid:pk>/',
        ClosetCategoryApiView.as_view(),
        name='closet_category_detail'
    ),

    # Subcategory APIs (ItemCategory)
    path(
        'closet-sub-category/',
        ClosetSubCategoryApiView.as_view(),
        name='closet_subcategory_list_create'
    ),
    path(
        'closet-sub-category/<uuid:pk>/',
        ClosetSubCategoryApiView.as_view(),
        name='closet_subcategory_detail'
    ),
    # path(
    #     'closet-subcetagary/',
    #     ClosetSubCategoryApiView.as_view(),
    #     name='closet_subcategory_list_create_alt'
    # ),
    # path(
    #     'closet-subcetagary/<uuid:pk>/',
    #     ClosetSubCategoryApiView.as_view(),
    #     name='closet_subcategory_detail_alt'
    # ),
]
