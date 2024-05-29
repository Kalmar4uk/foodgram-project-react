from django.contrib.auth import get_user_model
from django.db import models

from recipes.constants import LEN_FIELD
from recipes.validators import validate_time_amount

User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=LEN_FIELD['MAX_LEN_NAME_TAG_ING_RECIP']
    )
    color = models.CharField('Цвет', max_length=LEN_FIELD['MAX_LEN_COLOR_TAG'])
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=LEN_FIELD['MAX_LEN_NAME_TAG_ING_RECIP']
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=LEN_FIELD['MAX_LEN_MEAS_UN_ING']
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recip(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название', max_length=LEN_FIELD['MAX_LEN_NAME_TAG_ING_RECIP']
    )
    image = models.ImageField(
        'Изображение', upload_to='recipes/image/', default=None
    )
    text = models.TextField('Описание')
    cooking_time = models.SmallIntegerField('Время приготовления (мин)')
    tags = models.ManyToManyField(Tag, verbose_name='Тег(-и)')
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecip')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class IngredientRecip(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recip = models.ForeignKey(
        Recip,
        on_delete=models.CASCADE,
        related_name='recips',
        verbose_name='Рецепт'
    )
    amount = models.SmallIntegerField(
        'Количество', validators=[validate_time_amount]
    )

    class Meta:
        verbose_name = 'Ингредиенты рецептов'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'Ингредиент {self.ingredient} в рецепте {self.recip}'


class FavoriteShoppingCardModel(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recip = models.ForeignKey(
        Recip, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'Рецепт {self.recip} добавлен у пользователя {self.author}'


class Favorite(FavoriteShoppingCardModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorited'


class ShoppingCart(FavoriteShoppingCardModel):

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        default_related_name = 'shopping_carts'
