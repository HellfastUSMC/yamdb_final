from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from . import pagination, serializers
from .filters import TitleFilter
from .permissions import IsAdmin, IsAuthorAdminModerator, ReadOnly
from api_yamdb import settings
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """Базовый класс для создания и редактирования объекта."""

    serializer_class = serializers.AdminEditSerializer
    permission_classes = [IsAdmin]
    pagination_class = pagination.DefaultPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    queryset = User.objects.all()
    lookup_field = "username"


class SelfEditApiView(RetrieveUpdateAPIView):
    serializer_class = serializers.UserEditSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class GetTokenApiView(TokenObtainPairView):
    serializer_class = serializers.TokenSerializer


class SignUpApiView(CreateAPIView):
    """Вьюха регистрации нового пользователя."""

    serializer_class = serializers.SignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        code = default_token_generator.make_token(user)

        mail_text = render_to_string(
            "users/confirmation_code.txt",
            {
                "username": user.username,
                "code": code,
            },
        )

        send_mail(
            "Ваш код подтверждения",
            mail_text,
            settings.FROM_EMAIL,
            [user.email],
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class BaseViewSet(viewsets.ModelViewSet):
    """Базовая вьюха."""
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = pagination.DefaultPagination


class ListCreateDestroyViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    """Вьюха для списка, создания и удаления."""

    lookup_field = "slug"
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = pagination.DefaultPagination
    search_fields = ("name",)
    filter_backends = (filters.SearchFilter,)


class CommentViewSet(BaseViewSet):
    """Вьюха для комментариев."""

    permission_classes = [IsAuthorAdminModerator | ReadOnly]
    serializer_class = serializers.CommentSerializer

    def _get_review(self):
        """Получение объекта Review."""
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(Review, pk=review_id, title__id=title_id)

    def get_queryset(self):
        review = self._get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(ListCreateDestroyViewSet):
    """Вьюха категорий."""

    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    """Вьюха жанров."""

    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(BaseViewSet):
    """Вьюха произведений."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    # Поскольку: Title QuerySet won't use Meta.ordering in
    # Django 3.1. Add .order_by('-name') to retain the current query.
    # то добавляем сортировку тут.
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all().order_by('-name')

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.TitleListSerializer

        return serializers.TitleSerializer


class ReviewViewSet(BaseViewSet):
    """Вьюха отзывов."""

    permission_classes = [IsAuthorAdminModerator | ReadOnly]
    serializer_class = serializers.ReviewSerializer

    def _get_title(self):
        """Получить объект Title."""
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self._get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self._get_title()
        serializer.save(
            author=self.request.user,
            title=title,
        )
