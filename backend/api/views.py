from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientFilter
from api.paginators import PageNumberLimitPagination
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeShowSerializer, RecipesSmallSerializer,
                             TagSerializer, UserSubscribeSerializer)
from foodgram import settings
from recipes.models import Follow, Ingredient, Recipe, Tag

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class CustomUserViewSet(UserViewSet):
    pagination_class = PageNumberLimitPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=UserSubscribeSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = self.get_object()
        try:
            exist_follow = author.following.get(user=request.user)
        except Follow.DoesNotExist:
            exist_follow = False

        if request.method == 'POST':
            if exist_follow or request.user == author:
                return Response(
                    {'errors': 'Ошибка подписки.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(user=request.user, author=author)
            return Response(
                self.get_serializer(author).data,
                status=status.HTTP_201_CREATED
            )
        if not exist_follow:
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        exist_follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        serializer_class=UserSubscribeSerializer,
        permission_classes=(IsAuthenticated,),
        pagination_class=PageNumberLimitPagination
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
        return Response(
            self.get_serializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeShowSerializer
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    ordering = ('-pub_date',)
    pagination_class = PageNumberLimitPagination

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return RecipeCreateSerializer
        return self.serializer_class

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (Ingredient.objects
                       .filter(ingredient_amount__recipe__carts=request.user)
                       .values('name')
                       .annotate(total=Sum('ingredient_amount__amount'))
                       .values('name', 'measurement_unit', 'total')
                       )
        text = 'Список покупок: \n \n'
        for ingredient in ingredients:
            amount = ingredient["total"]
            text += (f'{ingredient["name"]} ({ingredient["measurement_unit"]})'
                     f' - {amount}\n')
        path = (f'{settings.MEDIA_ROOT}\\list_ingedients\\'
                f'{request.user.username}_list_of_buy.txt')
        with open(path, 'w') as file:
            file.write(text)
        return FileResponse(open(path, 'rb'), status=status.HTTP_200_OK)

    def post_delete_mtm_user(self, request, field):
        recipe = self.get_object()
        recipe_field = getattr(recipe, field)
        user = request.user
        exist = user in recipe_field.all()
        if request.method == 'POST':
            if exist:
                return Response(
                    {'error': 'Уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe_field.add(user)
            return Response(
                self.get_serializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        if not exist:
            return Response(
                {'error': 'Не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe_field.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=RecipesSmallSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.post_delete_mtm_user(request, 'favorites')

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=RecipesSmallSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.post_delete_mtm_user(request, 'carts')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.image.delete(save=False)
        instance.delete()
