import csv
import uuid

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.filters import IngredientSearchFilter
from recipes.models import (Ingredient, Link, Recipe, Tag, UserFavourite,
                            UserShoppingCart)
from recipes.permissions import IsOwner
from recipes.serializers import (IngredientSerializer, RecipeCreateSerializer,
                                 RecipeSerializer, TagSerializer,
                                 UserFavouriteSerializer,
                                 UserShoppingCartSerializer)
from recipes.utils import get_ingridients_in_shop_cart


class RecipeViewSet(viewsets.ModelViewSet):
    ordering = ('-pub_date',)
    permission_classes = [IsOwner]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        tags_slugs = self.request.GET.getlist('tags')
        is_favorited = self.request.GET.get('is_favorited')
        is_in_shopping_cart = self.request.GET.get('is_in_shopping_cart')
        author_id = self.request.GET.get('author')
        queryset = Recipe.objects.all()
        if self.request.user.is_authenticated and is_favorited:
            queryset = queryset.filter(
                userfavorites__user=self.request.user
            )
        if self.request.user.is_authenticated and is_in_shopping_cart:
            queryset = queryset.filter(
                usershoppingcart__user=self.request.user
            )
        if tags_slugs:
            queryset = queryset.filter(tags__slug__in=tags_slugs)
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        return queryset.distinct()

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to_favorites(request, pk)
        else:
            return self.remove_from_favorites(request, pk)

    def add_to_favorites(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                {'error': 'Такого рецепта не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            UserFavourite.objects.get(user=user, recipe=recipe)
        except UserFavourite.DoesNotExist:
            userfavourite = UserFavourite.objects.create(
                user=user, recipe=recipe
            )
            serializer = UserFavouriteSerializer(
                userfavourite,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def remove_from_favorites(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_fav_recipe = UserFavourite.objects.get(
                user=user, recipe=recipe
            )
        except UserFavourite.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_fav_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, pk)
        else:
            return self.remove_from_shopping_cart(request, pk)

    def add_to_shopping_cart(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                {'error': 'Такого рецепта не существует.'},
                status=status.HTTP_404_NOT_FOUND
            )
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            UserShoppingCart.objects.get(user=user, recipe=recipe)
        except UserShoppingCart.DoesNotExist:
            usershoppingcart = UserShoppingCart.objects.create(
                user=user, recipe=recipe
            )
            serializer = UserShoppingCartSerializer(
                usershoppingcart,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def remove_from_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            recipe_in_shopping_card = UserShoppingCart.objects.get(
                user=user, recipe=recipe
            )
        except UserShoppingCart.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe_in_shopping_card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        response = HttpResponse(content_type='text/csv', charset='utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="ingredients_to_buy.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(['Ingredient', 'Total Amount', 'Measurement Unit'])
        for ingredient_name, details in get_ingridients_in_shop_cart(
            user
        ).items():
            writer.writerow(
                [ingredient_name, details['amount'], details['unit']]
            )
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        base_link = request.build_absolute_uri('/')
        long_link = f"{base_link}recipes/{pk}"
        try:
            link = Link.objects.get(long_link=long_link)
        except Link.DoesNotExist:
            short_link = generate_short_link(base_link)
            link = Link.objects.create(
                long_link=long_link,
                short_link=short_link
            )
        return Response({'short-link': link.short_link})


def generate_short_link(base_link):
    unique_id = uuid.uuid4().hex[:5]
    short_link = f"{base_link}s/{unique_id}/"
    return short_link


@api_view(['GET'])
def redirect_from_short_link(request, slug=None):
    link = get_object_or_404(Link, short_link=request.build_absolute_uri())
    return redirect(link.long_link)


class IngredientViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class TagViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
