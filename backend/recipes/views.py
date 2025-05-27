from rest_framework import viewsets, permissions, filters
from .models import Recipe, Ingredient
from .serializers import (RecipeCreateSerializer,
                          IngredientSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    #filter_backends = [filters.SearchFilter]
    pagination_class = None
    #search_fields = ['^name']  # 👈 поиск по началу строки

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


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
