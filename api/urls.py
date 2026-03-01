from django.urls import path, include


urlpatterns = [
    path(
        'user/',
        include('users.api.urls')
    ),
    path(
        'closet/',
        include('closet.api.urls')
    ),
]