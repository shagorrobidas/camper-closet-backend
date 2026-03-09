from django.urls import path, include


urlpatterns = [
    path('user/', include('users.api.urls')),
    path('closet/', include('closet.api.urls')),
    path('dashboard/', include('dashboard.api.urls')),
    path('packing/', include('packing.api.urls')),
]