from rest_framework import pagination


class UserResultsSetPagination(pagination.CursorPagination):
    page_size = 5