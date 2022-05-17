from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserRole:
    """Кастомные пользовательские роли."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class CustomUserManager(UserManager):
    """Кастомный менеджер пользователей."""

    def create_superuser(
        self,
        username,
        email=None,
        password=None,
        role=UserRole.ADMIN,
        **kwargs,
    ):
        """Создание суперпользователя."""
        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            role=role,
            **kwargs,
        )


class User(AbstractUser):
    """Кастомная модель пользователя."""

    ROLES = [
        (UserRole.USER, "Пользователь"),
        (UserRole.MODERATOR, "Модератор"),
        (UserRole.ADMIN, "Администратор"),
    ]

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    objects = CustomUserManager()
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        max_length=254
    )
    bio = models.TextField(null=True, blank=True)
    role = models.CharField(
        max_length=10,
        choices=ROLES,
        default=UserRole.USER
    )

    class Meta:
        ordering = ["-id"]
