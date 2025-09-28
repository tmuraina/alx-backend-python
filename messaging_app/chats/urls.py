# messaging_app/chats/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from . import auth

# Create a router for ViewSets (if you have any)
router = DefaultRouter()

# Register your ViewSets here when you create them
# Example: router.register(r'conversations', views.ConversationViewSet)
# Example: router.register(r'messages', views.MessageViewSet)

urlpatterns = [
    # Authentication endpoints
    path('register/', auth.register_user, name='register'),
    path('login/', auth.login_user, name='login'),
    path('logout/', auth.logout_user, name='logout'),
    path('profile/', auth.user_profile, name='profile'),
    
    # Add your other app endpoints here when you create them
    # Example: path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list'),
    # Example: path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    # Example: path('messages/', views.MessageListCreateView.as_view(), name='message-list'),
    # Example: path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
] + router.urls
