from django.contrib import admin

from .models import Follow, Ingredient, IngredientAmount, Recipe, Tag


class IngredientCountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    min_num = 1


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    inlines = (IngredientCountInline,)


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('get_favorite_count',)
    filter_horizontal = ('ingredients', 'tags', 'favorites', 'carts')
    inlines = (IngredientCountInline,)

    @admin.display(description='Количество добавлений в избранное')
    def get_favorite_count(self, obj):
        return obj.favorites.count()
