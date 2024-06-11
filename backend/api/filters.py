from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class RecipesFilter(filters.FilterSet):
    author = filters.NumberFilter(
        field_name='author__id', lookup_expr='icontains'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.NumberFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.NumberFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        models = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_filter(self, queryset, name, value):
        if not value or self.request.user.is_anonymous:
            return queryset
        return queryset.filter(favorited__author=self.request.user)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if not value or self.request.user.is_anonymous:
            return queryset
        return queryset.filter(shopping_carts__author=self.request.user)
