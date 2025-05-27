from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet
from django.urls import path, include
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
