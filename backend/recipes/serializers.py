from rest_framework import serializers
from .models import Recipe, Ingredient, RecipeIngredient
from .fields import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError('Ингредиент с таким id не найден.')
        return value


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'cooking_time', 'ingredients', 'image')

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Нужно указать хотя бы один ингредиент.')
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError('Ингредиенты не должны повторяться.')
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)  # автор уже в validated_data

        recipe_ingredients = []
        for item in ingredients_data:
            ingredient = Ingredient.objects.get(id=item['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=item['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

