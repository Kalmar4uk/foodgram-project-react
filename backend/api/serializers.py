from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api import fields
from recipes.constants import LEN_FIELD
from recipes.models import (Favorite, Ingredient, IngredientRecip, Recip,
                            ShoppingCart, Subscription, Tag, User)


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

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
        read_only_true = ('username',)

    def get_is_subscribed(self, value):
        request = self.context.get('request')
        subscribed = Subscription.objects.filter(
            following=value.id, user=request.user.id
        ).exists()
        return subscribed


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=LEN_FIELD['MAX_LEN_EMAIL'])
    first_name = serializers.CharField(
        max_length=LEN_FIELD['MAX_LEN_FIRST_LAST_NAME']
    )
    last_name = serializers.CharField(
        max_length=LEN_FIELD['MAX_LEN_FIRST_LAST_NAME']
    )
    password = serializers.CharField(
        max_length=LEN_FIELD['MAX_LEN_PASSWORD'], write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def validate_password(self, data):
        validate_password(data)
        return data

    def validate_email(self, data):
        if User.objects.filter(email=data):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate_current_password(self, data):
        user = self.context['request'].user
        if not user.check_password(data):
            raise serializers.ValidationError(
                'Введен некорректный текущий пароль!'
            )
        return data

    def validate_new_password(self, data):
        validate_password(data)
        return data


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        required=True)
    password = serializers.CharField(
        required=True
    )

    class Meta:
        model = User
        fields = ('password', 'email')

    def validate_email(self, data):
        if not User.objects.filter(email=data):
            raise serializers.ValidationError(
                'Введен некорректный email!'
            )
        return data

    def validate(self, data):
        user = get_object_or_404(User, email=data['email'])
        if not user.check_password(data['password']):
            raise serializers.ValidationError(
                'Введен некорректный пароль!'
            )
        return data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recip.name')
    cooking_time = serializers.ReadOnlyField(source='recip.cooking_time')
    image = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, value):
        return str(value.recip.image)

    def validate(self, value):
        recip_id = self.context.get('view').kwargs.get('id')
        if not Recip.objects.filter(id=recip_id).exists():
            raise serializers.ValidationError(
                'Рецепта с таким id не существует'
            )
        return value


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart

    def validate(self, value):
        request = self.context.get('request')
        recip_id = self.context.get('view').kwargs.get('id')
        if ShoppingCart.objects.filter(author=request.user, recip=recip_id):
            raise serializers.ValidationError(
                'Нельзя повторно добавить рецепт в корзину'
            )
        return super().validate(value)


class FavoriteSerializer(FavoriteShoppingCartSerializer):

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite

    def validate(self, value):
        request = self.context.get('request')
        recip_id = self.context.get('view').kwargs.get('id')
        if Favorite.objects.filter(author=request.user, recip=recip_id):
            raise serializers.ValidationError(
                'Нельзя повторно добавить рецепт в избранное'
            )
        return super().validate(value)


class IngredientRecipSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecip
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipSerializer(serializers.ModelSerializer):
    tags = fields.TagFieldSerializer(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientRecipSerializer(many=True, source='recips')
    author = UserListSerializer(read_only=True)
    image = fields.Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recip
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
            'cooking_time',
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, value):
        request = self.context.get('request')
        is_favorited = Favorite.objects.filter(
            author=request.user.id, recip=value.id
        ).exists()
        return is_favorited

    def get_is_in_shopping_cart(self, value):
        request = self.context.get('request')
        is_in_shopping_cart = ShoppingCart.objects.filter(
            author=request.user.id,
            recip=value.id
        ).exists()
        return is_in_shopping_cart


class RecipWriteSerializer(serializers.ModelSerializer):
    tags = fields.TagFieldSerializer(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientRecipSerializer(many=True)
    author = UserListSerializer(read_only=True)
    image = fields.Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recip
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
            'cooking_time',
        )
        read_only_fields = ('author',)

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тег'
            )
        tags = []
        for tag in value:
            if tag.id in tags:
                raise serializers.ValidationError(
                    'Нельзя добавлять повторяющиеся теги'
                )
            tags.append(tag.id)
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент'
            )
        ingredients = []
        for ingredient in value:
            if ingredient.get('id') in ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальны'
                )
            ingredients.append(ingredient.get('id'))
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше одной минуты'
            )
        return value

    def validate(self, value):
        if (
            not value.get('ingredients') or not value.get('tags')
            or not value.get('name') or not value.get('text')
            or not value.get('image')
        ):
            raise serializers.ValidationError(
                'Отсутствует обязательное поле'
            )
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recip = Recip.objects.create(**validated_data)
        recip.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecip.objects.create(
                recip=recip,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recip

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        IngredientRecip.objects.filter(recip=instance).delete()
        for ingredient in ingredients:
            IngredientRecip.objects.create(
                recip=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipForSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recip
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserListSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = (
            'email', 'username', 'first_name', 'last_name', 'is_subscribed'
        )

    def get_recipes(self, value):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = Recip.objects.filter(
                author=value.id
            )[:int(recipes_limit)]
        else:
            recipes = Recip.objects.filter(author=value.id)
        serializer = RecipForSubscriptionSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, value):
        return Recip.objects.filter(author=value.id).count()

    def validate(self, value):
        user = self.context.get('request').user.id
        author = self.context.get(
            'request'
        ).parser_context.get('kwargs').get('pk')

        if Subscription.objects.filter(user=user, following=author).exists():
            raise serializers.ValidationError(
                'Подписка на автора уже форомлена'
            )
        if int(author) == user:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя'
            )
        return value
