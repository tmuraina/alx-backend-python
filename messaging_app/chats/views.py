# messaging_app/chats/views.py

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsParticipantOfConversation

from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserSummarySerializer,
    ConversationSerializer,
    ConversationSummarySerializer,
    MessageSerializer,
    MessageSummarySerializer,
    LoginSerializer,
    ChangePasswordSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class for consistent API responses."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Provides CRUD operations for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'username']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    filterset_fields = ['role', 'is_active']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['list']:
            return UserSummarySerializer
        return UserSerializer
    
    def get_permissions(self):
        """Custom permissions based on action."""
        if self.action == 'create':
            # Allow registration without authentication
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only allow users to modify their own profile or admin
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = User.objects.all()
        
        # Non-admin users can only see active users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password."""
        user = self.get_object()
        
        # Only allow users to change their own password or admin
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only change your own password.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password updated successfully.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation model.
    Provides CRUD operations for conversations with proper filtering.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'last_message_at']
    ordering = ['-last_message_at', '-created_at']
    filterset_fields = ['is_active']
    
    def get_queryset(self):
        """Return conversations where current user is a participant."""
        return Conversation.objects.filter(
            participants=self.request.user,
            is_active=True
        ).prefetch_related(
            Prefetch('participants', queryset=User.objects.all()),
            Prefetch('messages', queryset=Message.objects.filter(is_deleted=False).order_by('-sent_at')[:10])
        ).distinct()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['list']:
            return ConversationSummarySerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """Create conversation and ensure current user is included as participant."""
        conversation = serializer.save()
        
        # Add current user as participant if not already included
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            conversation.participants.add(self.request.user)
        
        return conversation
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.add_participant(user)
            
            return Response({
                'message': f'User {user.full_name} added to conversation.',
                'conversation': ConversationSummarySerializer(conversation, context={'request': request}).data
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            
            # Prevent removing yourself if you're the only participant
            if conversation.participants.count() <= 2 and user == request.user:
                return Response(
                    {'error': 'Cannot remove yourself from a conversation with only 2 participants.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conversation.remove_participant(user)
            
            return Response({
                'message': f'User {user.full_name} removed from conversation.',
                'conversation': ConversationSummarySerializer(conversation, context={'request': request}).data
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark all messages in conversation as read for current user."""
        conversation = self.get_object()
        
        # Mark all unread messages as read (excluding user's own messages)
        unread_messages = conversation.messages.filter(
            is_read=False,
            is_deleted=False
        ).exclude(sender=request.user)
        
        unread_count = unread_messages.count()
        unread_messages.update(is_read=True)
        
        return Response({
            'message': f'Marked {unread_count} messages as read.',
            'conversation_id': str(conversation.conversation_id)
        })


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message model.
    Provides CRUD operations for messages with conversation filtering.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['message_body']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    filterset_fields = ['is_read', 'conversation']
    
    def get_queryset(self):
        """Return messages from conversations where user is a participant."""
        conversation_id = self.request.query_params.get('conversation_id', None)
        
        # Base queryset: messages from conversations where user is participant
        queryset = Message.objects.filter(
            conversation__participants=self.request.user,
            is_deleted=False
        ).select_related('sender', 'conversation').distinct()
        
        # Filter by specific conversation if provided
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['list']:
            return MessageSummarySerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """Create message with current user as sender."""
        # Set sender to current user
        serializer.save(sender=self.request.user)
    
    def perform_update(self, serializer):
        """Update message with edited timestamp."""
        from django.utils import timezone
        serializer.save(edited_at=timezone.now())
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete message instead of hard delete."""
        message = self.get_object()
        
        # Only allow sender to delete their own messages
        if message.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.soft_delete()
        return Response({'message': 'Message deleted successfully.'})
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific message as read."""
        message = self.get_object()
        
        # Don't mark your own messages as read
        if message.sender == request.user:
            return Response(
                {'error': 'Cannot mark your own message as read.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.mark_as_read()
        
        return Response({
            'message': 'Message marked as read.',
            'message_id': str(message.message_id)
        })
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get all unread messages for current user."""
        unread_messages = self.get_queryset().filter(
            is_read=False
        ).exclude(sender=request.user)
        
        serializer = MessageSummarySerializer(
            unread_messages,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': unread_messages.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all unread messages as read for current user."""
        unread_messages = self.get_queryset().filter(
            is_read=False
        ).exclude(sender=request.user)
        
        count = unread_messages.count()
        unread_messages.update(is_read=True)
        
        return Response({
            'message': f'Marked {count} messages as read.'
        })


# Authentication Views (if needed)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view using email instead of username.
    """
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSummarySerializer(user).data
        })
