from rest_framework import serializers
from .models import Recipe, Ingredient, RecipeIngredient
from .fields import Base64ImageField


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError('Ингредиент не найден.')
        return value


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()
    name = serializers.CharField(max_length=256)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'cooking_time', 'ingredients', 'image')

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError('Ингредиенты не должны повторяться.')
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        bulk = []
        for item in ingredients_data:
            ingredient = Ingredient.objects.get(id=item['id'])
            bulk.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=item['amount']
            ))
        RecipeIngredient.objects.bulk_create(bulk)
        return recipe