from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Кастомный пермишен, который расширит возможности встроенных пермишенов
    и разрешит полный доступ к объекту только админу(суперюзеру)"""

    def has_permission(self, request, view):

        user = request.user

        return (
            user.is_authenticated and user.is_admin
            or user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен, который даст доступ на уровне админа"""

    def has_permission(self, request, view):

        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin
            )
        )


class UserIsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен, дающий доступ ко всем действиям только автору."""

    def has_object_permission(self, request, view, obj):

        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)
