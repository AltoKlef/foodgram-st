# api/urls.py

from django.urls import path, include

urlpatterns = [
    path('recipes/', include('recipes.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
