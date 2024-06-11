from django.urls import include, path
from rest_framework import routers

from api.views import (APIToken, DeleteApiToken, FavoriteRecipeView,
                       IngredientViewSet, RecipeViewSet, ShoppingCartFile,
                       ShoppingCartView, TagViewSet, UpdateUserPassword,
                       UserViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('users', UserViewSet)

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
        'recipes/<int:recipe_id>/favorite/',
        FavoriteRecipeView.as_view(),
        name='favorited'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart'
    ),
    path('auth/token/', include(auth_urls)),
    path(
        'users/set_password/',
        UpdateUserPassword.as_view(),
        name='set_password'
    ),
    path('', include(router_v1.urls)),
]
