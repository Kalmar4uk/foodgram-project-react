from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientRecip, Recip,
                            ShoppingCart, Subscription, Tag)


class IngredientRecipInline(admin.StackedInline):
    model = IngredientRecip
    extra = 0
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Recip)
class RecipAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipInline,)
    list_display = (
        'name',
        'get_ingredients',
        'get_tags',
        'cooking_time',
        'author',
        'pub_date',
    )
    list_filter = ('name', 'cooking_time', 'tags')
    search_fields = ('name',)
    filter_horizontal = ('tags',)

    @admin.display(description='Тег(-и)')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('color', 'slug')
    list_editable = ('color',)
    search_fields = ('name',)


@admin.register(IngredientRecip)
class IngredientRecipAdmin(admin.ModelAdmin):
    list_display = ('recip', 'ingredient', 'amount')
    list_filter = ('recip', 'amount')
    search_fields = ('recip', 'ingredient')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_filter = ('recip',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_filter = ('recip',)
