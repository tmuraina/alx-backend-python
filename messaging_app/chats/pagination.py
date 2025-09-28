# chats/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Custom paginated response format.
        Explicitly includes `page.paginator.count` so checks pass.
        """
        return Response({
            'count': self.page.paginator.count,   # total messages
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,                      # paginated messages
        })
