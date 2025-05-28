from rest_framework import serializers
from .models import Recipe, Ingredient, RecipeIngredient
from .fields import Base64ImageField
from django.db import transaction

class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    Используется для отображения списка ингредиентов с полями:
    id, name, measurement_unit.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.Serializer):
    """
    Сериализатор для получения данных об ингредиентах в рецепте
    при создании/редактировании рецепта.
    Принимает id ингредиента и его количество.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения ингредиента в рецепте (на чтение).
    Отображает вложенные данные ингредиента:
    id, name, measurement_unit и amount.
    Используется в RecipeReadSerializer.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения рецептов.
    Отображает список ингредиентов (через IngredientInRecipeSerializer)
    и изображение в виде base64.
    """
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_links',
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'text', 'image',
            'cooking_time', 'ingredients'
        ]


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    Принимает список ингредиентов (id и amount)
    через IngredientAmountSerializer
    и изображение в формате base64.
    """
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'text', 'image',
            'cooking_time', 'ingredients'
        ]

    def create_ingredients(self, ingredients_data, recipe):
        """
        Создаёт записи в промежуточной таблице RecipeIngredient
        на основе переданных ингредиентов и количества.
        Используется при создании и обновлении рецепта.
        """
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ])

    def create(self, validated_data):
        """
        Создание нового рецепта.
        Извлекает ингредиенты из validated_data,
        создаёт рецепт и связывает ингредиенты.
        """
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        with transaction.atomic():
            instance.save()
            if ingredients_data is not None:
                instance.ingredients.clear()  # Или .all().delete(), если нужно
                self.create_ingredients(ingredients_data, instance)

        return instance



