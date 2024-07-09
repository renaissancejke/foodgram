from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (MAX_LENGTH_INGREDIENT, MAX_LENGTH_LONG_LINK,
                               MAX_LENGTH_MEAS_UNIT, MAX_LENGTH_RECIPE,
                               MAX_LENGTH_SHORT_LINK, MAX_LENGTH_TAG,
                               MAX_LENGTH_TAG_SLUG)

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    name = models.CharField(max_length=MAX_LENGTH_RECIPE,
                            verbose_name='Название',
                            help_text='Введите название блюда, '
                                      f'не более {MAX_LENGTH_RECIPE} символов')
    text = models.TextField(verbose_name='Описание',
                            help_text='Введите описание блюда, '
                                         'не более 256 символов')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='IngredientRecipe',
                                         verbose_name='Ингредиенты',
                                         help_text='Выберите ингредиенты '
                                                      'из списка')
    image = models.ImageField(upload_to='recipes/images',
                              verbose_name='Картинка',
                              default=None)
    tags = models.ManyToManyField('Tag',
                                  verbose_name='Теги',
                                  through='TagRecipe')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            limit_value=1,
            message='Значение должно быть не меньше 1'
        )],
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True,
        help_text='Дата и время публикации.'
    )

    def __str__(self):
        return self.name

    def favourite_count(self):
        return UserFavourite.objects.filter(
            recipe=self
        ).count()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class Tag(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_TAG,
                            unique=True,
                            verbose_name='Название',
                            help_text='Название должно быть уникальным')
    slug = models.SlugField(max_length=MAX_LENGTH_TAG_SLUG,
                            unique=True,
                            verbose_name='Слаг',
                            help_text='Слаг должен быть уникальным')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT,
        verbose_name='Название',
        help_text='Введите название ингредиента, '
                  f'не более {MAX_LENGTH_INGREDIENT} символов'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEAS_UNIT,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения, не более '
                  f'{MAX_LENGTH_MEAS_UNIT}символов'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredients = models.ForeignKey(Ingredient,
                                    on_delete=models.CASCADE,
                                    verbose_name='Ингредиенты'
                                    )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='recipe_ingredient')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(
            limit_value=1,
            message='Значение должно быть не меньше 1'
        )],
        verbose_name='Количество',)

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.ingredients}-{self.recipe}'


class TagRecipe(models.Model):
    tags = models.ForeignKey(Tag,
                             on_delete=models.CASCADE,
                             verbose_name='Теги')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='recipe_tag')

    class Meta:
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.tags}-{self.recipe}'


class UserFavourite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='userfavorites')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Избранные рецепты',
                               related_name='userfavorites')

    class Meta:
        verbose_name = 'избранный рецепт пользователя'
        verbose_name_plural = 'Избранные рецепты пользователя'

    def __str__(self):
        return f'{self.user}-{self.recipe}'


class UserShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='usershoppingcart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Список покупок',
                               related_name='usershoppingcart')

    class Meta:
        verbose_name = 'корзина пользователя'
        verbose_name_plural = 'Продукты в корзинах подьзователей'

    def __str__(self):
        return f'{self.user}-{self.recipe}'


class Link(models.Model):
    short_link = models.CharField(max_length=MAX_LENGTH_SHORT_LINK)
    long_link = models.CharField(max_length=MAX_LENGTH_LONG_LINK)

    class Meta:
        verbose_name = 'ссылка на рецепт'
        verbose_name_plural = 'Ссылки на рецепт'

    def __str__(self):
        return f'{self.short_link}-{self.long_link}'
