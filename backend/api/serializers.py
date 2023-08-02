from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class UserCreateCustomSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Email должен быть уникальным'
        )],
        max_length=254
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all(),
                            message='Username должен быть уникальным'),
            RegexValidator(regex=r'^[\w.@+-]+\Z',
                           message='Неверные символы в username')
        ]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(
        max_length=150,
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        return obj.following.filter(user=request.user).exists()


class RecipesSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = int(
            request.query_params.get('recipes_limit', obj.recipes.count())
        )
        recipes = obj.recipes.all()[:recipes_limit]
        return RecipesSmallSerializer(many=True).to_representation(recipes)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects, source='ingredient.id'
    )
    amount = serializers.IntegerField(min_value=1)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeShowSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredient_amount'
    )
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user in obj.favorites.all()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user in obj.carts.all()


class RecipeCreateSerializer(RecipeShowSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    def add_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']['id']
            amount = ingredient_data['amount']
            recipe.ingredients.add(
                ingredient, through_defaults={'amount': amount}
            )
        return recipe

    def create(self, validated_data):
        ingredients_amounts = validated_data.pop('ingredient_amount')
        recipe = super().create(validated_data)
        return self.add_ingredients(recipe, ingredients_amounts)

    def update(self, instance, validated_data):
        ingredients_amounts = validated_data.pop('ingredient_amount')
        if validated_data.get('image') is not None:
            instance.image.delete(save=False)
        recipe = super().update(instance, validated_data)
        recipe.ingredients.clear()
        return self.add_ingredients(recipe, ingredients_amounts)
