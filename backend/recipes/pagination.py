from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class RecipesPagination(PageNumberPagination):
    page_size = 6

    def get_paginated_response(self, data):
        return Response(data)
