from django.urls import include, path
from rest_framework import routers

from api.views import (APIToken, DeleteApiToken, FavoriteRecipView,
                       IngredientViewSet, RecipViewSet, ShoppingCartFile,
                       ShoppingCartView, TagViewSet, UpdateUserPassword,
                       UserViewSet)

router = routers.DefaultRouter()
router.register('recipes', RecipViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)

auth_urls = [
    path('login/', APIToken.as_view(), name='token_create'),
    path('logout/', DeleteApiToken.as_view(), name='token_delete'),
]

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartFile.as_view(),
        name='download_file'
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavoriteRecipView.as_view(),
        name='favorited'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart'
    ),
    path('auth/token/', include(auth_urls)),
    path(
        'users/set_password/',
        UpdateUserPassword.as_view(),
        name='set_password'
    ),
    path('', include(router.urls)),
]
