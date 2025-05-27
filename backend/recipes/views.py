from rest_framework import viewsets, permissions
from .models import Recipe
from .serializers import RecipeCreateSerializer


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
