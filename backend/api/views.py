from rest_framework import viewsets

from api.serializers import TagSerializer, IngredientSerializer
from recipes.models import Tag, Ingredient


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
