from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, ShortLinkRedirectView
from django.urls import path, include
router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/s/<str:code>/',
        ShortLinkRedirectView.as_view(),
        name='short-link'
    ),
]
