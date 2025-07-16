from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение, разрешающее только автору объекта
    редактировать или удалять его.
    Остальным пользователям доступно только чтение.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем
        return (request.method in SAFE_METHODS) or (obj.author == request.user)
