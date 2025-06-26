from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение, разрешающее только автору объекта
    редактировать или удалять его.
    Остальным пользователям доступно только чтение.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем
        if request.method in SAFE_METHODS:
            return True
        # Разрешаем небезопасные методы только автору
        return obj.author == request.user
