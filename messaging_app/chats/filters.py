# chats/filters.py
import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter by participant username
    participant = django_filters.CharFilter(
        field_name="conversation__participants__username",
        lookup_expr="icontains"
    )

    # Filter by time range
    start_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Message
        fields = ['participant', 'start_date', 'end_date']
