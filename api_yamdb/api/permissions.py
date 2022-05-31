from api_yamdb.settings import EXC_NAME
from rest_framework import permissions

from api.exceptions import CodeAPIException


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            return (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            )
        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if 'username' not in request.parser_context['kwargs']:
            return request.user.is_admin
        if request.parser_context['kwargs']['username'] != EXC_NAME:
            return request.user.is_admin
        if request.method not in ('GET', 'PATCH'):
            raise CodeAPIException(
                detail='Запрещенный метод', status_code=405)
        return True


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated:
            return request.user.is_admin
        return False
