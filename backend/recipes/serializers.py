from rest_framework import serializers
from collections import Counter
from .models import Recipe, Ingredient, RecipeIngredient
from core.fields import Base64ImageField

from users.serializers import CustomUserListSerializer


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


class RecipeIngredientSerializer(serializers.ModelSerializer):
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
    Отображает список ингредиентов, автора, флаг избранного и корзины.
    """
    ingredients = RecipeIngredientSerializer(
        source='ingredients_links',
        many=True
    )
    image = Base64ImageField()
    author = CustomUserListSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'text', 'image',
            'cooking_time', 'ingredients',
            'author', 'is_favorited', 'is_in_shopping_cart'
        ]

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.in_shopping_carts.filter(user=user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    Принимает список ингредиентов (id и amount)
    через IngredientAmountSerializer
    и изображение в формате base64.
    """
    ingredients = IngredientAmountSerializer(many=True, required=True)
    image = Base64ImageField(required=True, allow_null=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'text', 'image',
            'cooking_time', 'ingredients'
        ]

    def validate(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно.'
            })
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        ids = [item['id'] for item in value]
        duplicates = [item for item, count in Counter(ids).items() if count > 1]
        if duplicates:
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def create_ingredients(self, ingredients_data, recipe):
        """
        Создаёт записи в промежуточной таблице RecipeIngredient
        на основе переданных ингредиентов и количества.
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

    def update_ingredients(self, recipe, ingredients_data):
        recipe.ingredients_links.all().delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ])

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            self.update_ingredients(instance, ingredients_data)

        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


