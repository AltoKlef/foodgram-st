# api/urls.py

from django.urls import include, path

urlpatterns = [
    path('', include('recipes.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', include('users.urls')),
]
