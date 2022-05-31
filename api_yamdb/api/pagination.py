from rest_framework.pagination import PageNumberPagination


class PostsPagination(PageNumberPagination):
    page_size = 5
