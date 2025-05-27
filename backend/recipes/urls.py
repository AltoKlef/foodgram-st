from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet
from django.urls import path, include
router = DefaultRouter()
router.register(r'', RecipeViewSet, basename='recipes')
urlpatterns = router.urls
'''urlpatterns = [
    path('', include(router.urls)),
]'''
