from django.db.models import Sum
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import SAFE_METHODS

from core.permissions import IsAuthorOrReadOnly
from core.serializers import ShortRecipeSerializer
from core.shortener import decode_base62, encode_base62
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart)
from recipes.serializers import (IngredientSerializer,
                                 RecipeReadSerializer, RecipeWriteSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def handle_recipe_relation(self, request, pk, model, error_text):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Рецепт уже {error_text}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted_count, _ = model.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if deleted_count != 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Рецепта нет {error_text}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        code = encode_base62(recipe.pk)
        relative_url = f'/api/recipes/s/{code}/'
        short_link = request.build_absolute_uri(relative_url)
        return Response({'short-link': short_link})

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self.handle_recipe_relation(
            request, pk, Favorite, 'в избранном'
        )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        return self.handle_recipe_relation(
            request, pk, ShoppingCart, 'в списке покупок'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts__user=user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = []
        for item in ingredients:
            line = (
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) — "
                f"{item['total']}"
            )
            lines.append(line)

        content = '\n'.join(lines)
        filename = 'shopping_list.txt'

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ShortLinkRedirectView(APIView):
    def get(self, request, code):
        try:
            recipe_id = decode_base62(code)
        except Exception:
            return HttpResponseNotFound("Invalid short code")

        recipe = get_object_or_404(Recipe, pk=recipe_id)
        return redirect(f'/api/recipes/{recipe.pk}/')
