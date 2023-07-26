from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, Tag, Recipe

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
