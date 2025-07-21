from rest_framework import serializers

from recipes.models import Recipe

from drf_extra_fields.fields import Base64ImageField

class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения краткой информации о рецепте
    Используется при добавлении и удалении из корзины
    """
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
