from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from core.permissions import IsAuthorOrReadOnly
from core.serializers import ShortRecipeSerializer
from core.shortener import decode_base62, encode_base62
from .models import (Recipe,
                     Ingredient,
                     Favorite,
                     ShoppingCart,
                     RecipeIngredient)

from .serializers import (RecipeReadSerializer,
                          RecipeWriteSerializer,
                          IngredientSerializer,
                          FavoriteRecipeSerializer)
from .filters import IngredientFilter, RecipeFilter


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
    # pagination_class = None

    def get_serializer_class(self):
        if self.request.method in ('GET',):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        read_serializer = RecipeReadSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()

        read_serializer = RecipeReadSerializer(
            recipe, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        code = encode_base62(recipe.pk)
        relative_url = f'/api/recipes/s/{code}/'
        short_link = request.build_absolute_uri(relative_url)
        return Response({'short-link': short_link})

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe)
            if cart_item.exists():
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
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
                recipe__in_shopping_carts__user=user
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
