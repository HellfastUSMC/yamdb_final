from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

import api.exceptions as ApiException
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
        read_only_fields = ("rewiew",)


class AdminEditSerializer(serializers.ModelSerializer):
    """Серилизатор User для редактирования админом."""

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name", "bio", "role"
        )


class UserEditSerializer(AdminEditSerializer):
    """Серилизатор User для редактирования пользователем."""

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name", "bio", "role"
        )
        read_only_fields = ("role",)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=200)
    confirmation_code = serializers.CharField(max_length=200)

    def validate(self, data):
        """Валидатор параметров получения токена."""
        user = get_object_or_404(User, username=data["username"])
        code = data["confirmation_code"]
        if not default_token_generator.check_token(user, code):
            raise ApiException.ConfirmationCodeError

        refresh = RefreshToken.for_user(user)

        return {"token": str(refresh.access_token)}


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""

    def validate_username(self, value):
        """Проверка имени пользователя."""
        if value == "me":
            raise ApiException.UserNameMeError
        return value

    class Meta:
        model = User
        fields = ("username", "email")


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )
    name = serializers.CharField(max_length=256)

    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )
    name = serializers.CharField(max_length=256)

    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    genre = serializers.SlugRelatedField(
        slug_field="slug", many=True, queryset=Genre.objects.all()
    )

    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Title

    def validate_year(self, value):
        year = dt.now()
        if not 0 < value <= year.year:
            raise ApiException.YearValidationError
        return value


class TitleListSerializer(TitleSerializer):
    """Сериализатор модели Title для представления списком."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer(many=False)
    rating = serializers.IntegerField(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username"
    )

    class Meta:
        exclude = ["title"]
        model = Review

    def validate_score(self, value):
        if not isinstance(value, int) or not 0 < value < 11:
            raise ApiException.ScoreValidationError
        return value

    def validate(self, data):
        request = self.context["request"]
        title_id = self.context["view"].kwargs.get("title_id")
        exists = Review.objects.filter(
            title__id=title_id, author=request.user
        ).exists()
        if exists and request.method == "POST":
            raise ApiException.ReviewUniqueExist
        return data
