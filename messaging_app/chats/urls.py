# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet, UserViewSet, CustomAuthToken

# Create router and register viewsets
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/login/', CustomAuthToken.as_view(), name='api_login'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
