

class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения краткой информации о рецепте
    Используется при добавлении и удалении из корзины
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')