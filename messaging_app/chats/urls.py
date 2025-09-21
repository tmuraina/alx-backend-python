# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet, UserViewSet, CustomAuthToken

# Create router and register viewsets
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'users', UserViewSet, basename='user')

# Create nested router for conversations and messages
conversations_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    
    # Authentication endpoints
    path('auth/login/', CustomAuthToken.as_view(), name='api_login'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
