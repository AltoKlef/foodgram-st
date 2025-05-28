from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Recipe, Ingredient
from .serializers import (RecipeReadSerializer,
                          RecipeWriteSerializer,
                          IngredientSerializer)
from .filters import IngredientFilter
# from .pagination import RecipesPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('GET',):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()  # сразу сохраняем

        read_serializer = RecipeReadSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)