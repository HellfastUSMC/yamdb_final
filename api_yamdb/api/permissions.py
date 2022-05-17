from rest_framework import permissions


class IsAdmin(permissions.IsAdminUser):
    """Разрешения только для админа."""

    message = "Вносить изменения может только администратор!"

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return request.user.is_superuser or request.user.is_admin


class IsAuthorAdminModerator(permissions.IsAuthenticatedOrReadOnly):
    """Доступ только для автора, модератора или админа."""

    message = "Вносить изменения может только автор, модератор или админ!"

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        return obj.author == user or user.is_admin or user.is_moderator


class ReadOnly(permissions.BasePermission):
    """Только просмотр."""

    message = "Только просмотр!"

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
