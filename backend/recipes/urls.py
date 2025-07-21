from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (IngredientViewSet, RecipeViewSet,
                           ShortLinkRedirectView)

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/s/<str:code>/',
        ShortLinkRedirectView.as_view(),
        name='short-link'
    ),
]
