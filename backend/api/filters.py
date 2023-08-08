from django_filters import CharFilter
from django_filters.rest_framework import (
    BooleanFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    NumberFilter,
)

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(method='get_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_shopping_cart')
    author = NumberFilter(field_name='author__id')
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def get_shopping_cart(self, queryset, name, value):
        user = self.request.user
        return (user.carts_recipes.all()
                if value and user.is_authenticated else queryset)

    def get_favorited(self, queryset, name, value):
        user = self.request.user
        return (user.favorite_recipes.all()
                if value and user.is_authenticated else queryset)


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
