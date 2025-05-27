# cats/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class RecipesPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        return Response(data)