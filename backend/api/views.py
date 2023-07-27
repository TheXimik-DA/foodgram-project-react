from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from api.serializers import TagSerializer, IngredientSerializer, \
    UserSubscribeSerializer
from recipes.models import Tag, Ingredient, Follow

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class CustomUserViewSet(UserViewSet):

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=UserSubscribeSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = self.get_object()
        exist_follow = Follow.objects.filter(
            user=request.user, author=author
        )
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
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        return Response(
            self.get_serializer(queryset, many=True).data,
            status=status.HTTP_200_OK
        )
