from django.urls import path
from closet.api.views import ItemCategoryListView

urlpatterns = [
    path(
        'item-categories/',
        ItemCategoryListView.as_view(),
        name='item-categories'
    ),
]
