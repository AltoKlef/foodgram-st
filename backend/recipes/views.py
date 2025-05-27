from rest_framework import viewsets, permissions
from .models import Recipe, Ingredient
from .serializers import (RecipeCreateSerializer,
                          IngredientSerializer)
from .filters import IngredientFilter
from .pagination import RecipesPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = RecipesPagination
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer  # <-- обязательно
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        print("AAAAAA")
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeCreateSerializer  # позже можно добавить RecipeListSerializer и т.п.

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
