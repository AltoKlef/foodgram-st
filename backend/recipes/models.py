# Create your models here.
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.constants import (IMAGE_UPLOAD_PATH, MAX_NAME_LENGTH, MAX_UOF_LENGTH,
                            MIN_COOKING_TIME)


class Ingredient(models.Model):

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_UOF_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_name_unit')]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to=IMAGE_UPLOAD_PATH,
        verbose_name='Изображение'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)],
        verbose_name='Время приготовления'
    )

    class Meta:
        ordering = ['name']
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'recipe', 'ingredient'
                ], name='unique_recipe_ingredient')
        ]
        verbose_name = 'Ингридент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецептах'
        ordering = ['ingredient__name']

    def __str__(self):
        return f'{self.ingredient} — {self.amount} for {self.recipe}'


class UserRecipeBase(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_unique_user_recipe'
            )
        ]
        ordering = ['-id']

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(UserRecipeBase):
    class Meta(UserRecipeBase.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class ShoppingCart(UserRecipeBase):
    class Meta(UserRecipeBase.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_carts'
