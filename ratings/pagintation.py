from rest_framework import pagination
from rest_framework.response import Response

class MovieRatingPagination(pagination.PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'is_reviewed': self.is_reviewed,
            'results': data
        })