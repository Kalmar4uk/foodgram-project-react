import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import RecipesFilter
from api.pagination import CustomPagination
from api.permissions import AuthorOnlyPermission
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipSerializer, RecipWriteSerializer,
                             ShoppingCartSerializer, SubscriptionsSerializer,
                             TagSerializer, TokenSerializer,
                             UpdateUserPasswordSerializer, UserListSerializer,
                             UserSerializer)
from recipes.models import (Favorite, Ingredient, IngredientRecip, Recip,
                            ShoppingCart, Subscription, Tag, User)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'delete']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSerializer
        return UserListSerializer

    @action(detail=False, url_path='me', permission_classes=(IsAuthenticated,))
    def get_users_info(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = UserListSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
            methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,)
        )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author, context={'request': request}, data=request.data
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, following=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user, following=author
            )
            if not subscription:
                return Response(
                    {'errors': 'Подписка не была оформлена'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class UpdateUserPassword(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = UpdateUserPasswordSerializer(
            context={'request': request}, data=request.data
        )
        self.user = request.user

        if serializer.is_valid():
            self.user.set_password(serializer.data.get('new_password'))
            self.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIToken(ObtainAuthToken):

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = get_object_or_404(User, email=email)
        token, created = Token.objects.get_or_create(user=user)
        if created:
            return Response(
                {'auth_token': str(token)}, status=status.HTTP_201_CREATED
            )
        return Response(
            {'auth_token': str(token)}, status=status.HTTP_200_OK
        )


class DeleteApiToken(APIView):

    def post(self, request):
        Token.objects.get(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipViewSet(viewsets.ModelViewSet):
    queryset = Recip.objects.all()
    serializer_class = RecipSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOnlyPermission)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipSerializer
        return RecipWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class FavoriteShoppingCardView(
    generics.CreateAPIView, generics.DestroyAPIView
):
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def get_recip(self):
        recip_id = self.kwargs.get('id')
        return get_object_or_404(Recip, pk=recip_id)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            recip=self.get_recip()
        )

    def perform_destroy(self, instance):
        instance.delete()


class FavoriteRecipView(FavoriteShoppingCardView):
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return self.get_recip().favorited.all()

    def destroy(self, request, *args, **kwargs):
        instance = Favorite.objects.filter(
            author=self.request.user, recip=self.get_recip()
        )
        if not instance:
            return Response(
                {'errors': 'Рецепт отсутствует в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(FavoriteShoppingCardView):
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        return self.get_recip().shopping_carts.all()

    def destroy(self, request, *args, **kwargs):
        instance = ShoppingCart.objects.filter(
            author=self.request.user, recip=self.get_recip()
        )
        if not instance:
            return Response(
                {'errors': 'Рецепт отсутствует в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartFile(APIView):

    def get(self, request):
        response = HttpResponse(
            content_type="text/csv",
            charset='utf-8-sig',
            headers={
                "Content-Disposition": 'attachment; filename="recipe.txt"'
            },
        )
        writer = csv.writer(response, delimiter=' ', quotechar='|')
        ingredients = IngredientRecip.objects.filter(
            recip__shopping_carts__author=request.user.id
        ).values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(
                    amount=Sum('amount')
                )
        for ingredient in ingredients:
            writer.writerow([
                f'{ingredient.get("ingredient__name")} '
                f'({ingredient.get("ingredient__measurement_unit")}) - '
                f'{ingredient.get("amount")}'
            ])
        return response
