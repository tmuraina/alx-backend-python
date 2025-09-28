
from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    page_size = 20                # default messages per page
    page_size_query_param = 'page_size'  # allow clients to override
    max_page_size = 100           # prevent abuse with very large page_size
