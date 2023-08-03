from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MIN_VALUE = 1
MAX_VALUE = 32000


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
        max_length=200
    )

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        'Ingredient',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_amount',

    )
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_amount'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество в рецепте',
        validators=[
            MinValueValidator(MIN_VALUE, 'Должно быть больше 0'),
            MaxValueValidator(MAX_VALUE, 'Максимальное количество - 32000')]
    )

    class Meta:
        verbose_name = 'Пропорция'
        verbose_name_plural = 'Пропорции'

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount} '
                f'{self.ingredient.measurement_unit}')


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe/images/',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1, blank=False,
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_VALUE,
                message='Время приготовления не может быть меньше минуты'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='32000 минут? Слишком много'
            ),
        )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    favorites = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        verbose_name='Избранное',
        blank=True
    )
    carts = models.ManyToManyField(
        User,
        related_name='carts_recipes',
        verbose_name='Корзина',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return (f'Рецепт: {self.name}, Автор: {self.author.first_name} '
                f'{self.author.last_name}')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ['-author_id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
