# messaging_app/chats/permissions.py

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has a 'user' field and if the request user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object has a 'sender' field (for messages)
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
            
        # Check if the object has a 'participants' field (for conversations)
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
            
        return False


class IsParticipantInConversation(BasePermission):
    """
    Custom permission to check if user is a participant in the conversation.
    """
    def has_object_permission(self, request, view, obj):
        # For conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For message objects, check if user is participant in the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
            
        return False


class IsMessageSenderOrConversationParticipant(BasePermission):
    """
    Custom permission for messages - allows access if user is the sender 
    or a participant in the conversation.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is the sender of the message
        if hasattr(obj, 'sender') and obj.sender == request.user:
            return True
            
        # Allow if user is a participant in the conversation
        if hasattr(obj, 'conversation') and hasattr(obj.conversation, 'participants'):
            return request.user in obj.conversation.participants.all()
            
        return False


class CanAccessConversation(BasePermission):
    """
    Permission to check if user can access a conversation.
    Users can only access conversations they are participants in.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()


class CanSendMessage(BasePermission):
    """
    Permission to check if user can send a message in a conversation.
    Users can only send messages to conversations they are participants in.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        # For POST requests (creating messages), check if user is participant
        if request.method == 'POST':
            conversation_id = request.data.get('conversation')
            if conversation_id:
                try:
                    from .models import Conversation  # Import here to avoid circular imports
                    conversation = Conversation.objects.get(id=conversation_id)
                    return request.user in conversation.participants.all()
                except Conversation.DoesNotExist:
                    return False
        
        return True


class IsAuthenticatedAndActive(BasePermission):
    """
    Custom permission to check if user is authenticated and active.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_active
        )


class IsOwnerOfProfile(BasePermission):
    """
    Permission to check if user can access their own profile.
    """
    def has_object_permission(self, request, view, obj):
        # Users can only access their own profile
        return obj == request.user


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation 
    to view, send, update, or delete messages.
    """

    def has_permission(self, request, view):
        # First, check if user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permission.
        Assuming `obj` is a Conversation or a Message with a FK to Conversation.
        """
        if hasattr(obj, "participants"):  
            # Conversation model with a participants many-to-many field
            return request.user in obj.participants.all()

        if hasattr(obj, "conversation"):  
            # Message model with a FK to Conversation
            return request.user in obj.conversation.participants.all()

        return False
