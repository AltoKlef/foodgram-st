from collections import Counter

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from users.serializers import CustomUserListSerializer

from recipes.models import Ingredient, Recipe, RecipeIngredient
from core.constants import MIN_INGREDIENT_AMOUNT, MIN_COOKING_TIME


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.

    Атрибуты
    ---------
    model : Ingredient
        Модель ингредиента
    fields : tuple
        Отображаемые поля: id, name, measurement_unit
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.Serializer):
    """
    Сериализатор для ингредиентов в рецепте.

    Применяется при создании или редактировании рецепта.

    Атрибуты
    ---------
    id : PrimaryKeyRelatedField
        Ссылка на объект ингредиента
    amount : IntegerField
        Количество ингредиента
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов рецепта (на чтение).

    Используется в RecipeReadSerializer. Отображает вложенные поля
    ингредиента: id, name, measurement_unit и amount.

    Атрибуты
    ---------
    id : ReadOnlyField
        Идентификатор ингредиента
    name : ReadOnlyField
        Название ингредиента
    measurement_unit : ReadOnlyField
        Единица измерения
    amount : IntegerField
        Количество ингредиента
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

    Отображает список ингредиентов, автора, флаг избранного и
    добавления в корзину.

    Атрибуты
    ---------
    ingredients : RecipeIngredientSerializer
        Список ингредиентов
    image : Base64ImageField
        Изображение рецепта
    author : CustomUserListSerializer
        Автор рецепта
    is_favorited : SerializerMethodField
        Признак избранного
    is_in_shopping_cart : SerializerMethodField
        Признак нахождения в корзине
    """
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    image = Base64ImageField(required=True, allow_null=False)
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

    def _check_user_relation(self, obj, related_manager):
        """Проверяет наличие рецепта в favorites или shopping_carts."""
        user = self.context.get('request').user
        return (user.is_authenticated
                and related_manager.filter(user=user).exists())

    def get_is_favorited(self, obj):
        """Возвращает True, если рецепт в избранном у пользователя."""
        return self._check_user_relation(obj, obj.favorites)

    def get_is_in_shopping_cart(self, obj):
        """Возвращает True, если рецепт в корзине пользователя."""
        return self._check_user_relation(obj, obj.favorites)


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.

    Принимает список ингредиентов (id и amount)
    через IngredientAmountSerializer
    и изображение в формате base64.

    Атрибуты
    ---------
    ingredients : IngredientAmountSerializer
        Список ингредиентов рецепта
    image : Base64ImageField
        Изображение рецепта
    cooking_time : IntegerField
        Время приготовления
    short_link : SerializerMethodField
        Короткая ссылка
    """
    ingredients = IngredientAmountSerializer(many=True, required=True)
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)
    short_link = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'text', 'image',
            'cooking_time', 'ingredients', 'short_link'
        ]

    def validate(self, data):
        """Проверка списка ингредиентов на наличие, пустоту и дубликаты."""
        ingredients = data.get('ingredients')
        if ingredients is None:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно.'
            })
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент.'
            })
        ids = [item['id'] for item in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться.'
            })
        return data

    def validate_image(self, value):
        """Проверка, что изображение не пустое."""
        if value is None:
            raise serializers.ValidationError('Изображение обязательно')
        return value

    def create_ingredients(self, ingredients_data, recipe):
        """Создаёт объекты связи рецепт-ингредиент."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ])

    def create(self, validated_data):
        """Создаёт рецепт и связывает его с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update_ingredients(self, recipe, ingredients_data):
        """Обновляет список ингредиентов у рецепта."""
        recipe.recipe_ingredients.all().delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ])

    def update(self, instance, validated_data):
        """Обновляет рецепт и его ингредиенты."""
        ingredients_data = validated_data.pop('ingredients')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            self.update_ingredients(instance, ingredients_data)

        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого представления рецепта.

    Используется в списке избранных рецептов.

    Атрибуты
    ---------
    image : Base64ImageField
        Изображение рецепта
    """
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
