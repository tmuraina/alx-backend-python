# messaging_app/chats/serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Handles user creation, updates, and representations.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'password',
            'password_confirm',
            'created_at',
            'is_active',
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True},
        }
    
    def validate(self, attrs):
        """Custom validation for password confirmation."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """Create user with encrypted password."""
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm', None)
        
        # Extract password and create user
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user, handling password separately."""
        # Remove password_confirm as it's not needed
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update password if provided
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for User model.
    Used in nested relationships to avoid circular references.
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role']
        read_only_fields = ['user_id']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    Includes sender information and handles message creation.
    """
    sender = UserSummarySerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)
    conversation_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'conversation_id',
            'message_body',
            'sent_at',
            'is_read',
            'is_deleted',
            'edited_at',
        ]
        read_only_fields = ['message_id', 'sent_at', 'edited_at']
    
    def validate(self, attrs):
        """Custom validation for message creation."""
        request = self.context.get('request')
        
        # If sender_id is not provided, use the authenticated user
        if not attrs.get('sender_id') and request and request.user.is_authenticated:
            attrs['sender_id'] = request.user.user_id
        
        # Validate that sender exists
        if attrs.get('sender_id'):
            try:
                sender = User.objects.get(user_id=attrs['sender_id'])
                attrs['sender'] = sender
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid sender_id.")
        
        # Validate that conversation exists
        if attrs.get('conversation_id'):
            try:
                conversation = Conversation.objects.get(conversation_id=attrs['conversation_id'])
                attrs['conversation'] = conversation
                
                # Validate that sender is a participant in the conversation
                if attrs.get('sender') and not conversation.participants.filter(user_id=attrs['sender'].user_id).exists():
                    raise serializers.ValidationError("Sender is not a participant in this conversation.")
                    
            except Conversation.DoesNotExist:
                raise serializers.ValidationError("Invalid conversation_id.")
        
        return attrs
    
    def create(self, validated_data):
        """Create message with proper relationships."""
        # Remove write-only fields that are handled in validation
        validated_data.pop('sender_id', None)
        validated_data.pop('conversation_id', None)
        
        return Message.objects.create(**validated_data)


class MessageSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Message model.
    Used in conversation listings to show recent messages.
    """
    sender = UserSummarySerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'message_body', 'sent_at', 'is_read']
        read_only_fields = ['message_id', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Conversation model.
    Includes full message history and participant details.
    """
    participants = UserSummarySerializer(many=True, read_only=True)
    participants_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True,
        help_text="List of user IDs to include as participants"
    )
    messages = MessageSerializer(many=True, read_only=True)
    participants_count = serializers.ReadOnlyField(source='get_participants_count')
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participants_ids',
            'participants_count',
            'messages',
            'last_message',
            'created_at',
            'last_message_at',
            'is_active',
        ]
        read_only_fields = ['conversation_id', 'created_at', 'last_message_at']
    
    def get_last_message(self, obj):
        """Get the most recent message in the conversation."""
        last_message = obj.messages.filter(is_deleted=False).order_by('-sent_at').first()
        if last_message:
            return MessageSummarySerializer(last_message).data
        return None
    
    def validate_participants_ids(self, value):
        """Validate that all participant IDs are valid users."""
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        
        # Check if all user IDs exist
        existing_users = User.objects.filter(user_id__in=value)
        if existing_users.count() != len(value):
            missing_ids = set(value) - set(existing_users.values_list('user_id', flat=True))
            raise serializers.ValidationError(f"Invalid user IDs: {list(missing_ids)}")
        
        return value
    
    def create(self, validated_data):
        """Create conversation with participants."""
        participants_ids = validated_data.pop('participants_ids')
        
        # Create conversation
        conversation = Conversation.objects.create(**validated_data)
        
        # Add participants
        participants = User.objects.filter(user_id__in=participants_ids)
        conversation.participants.set(participants)
        
        return conversation
    
    def update(self, instance, validated_data):
        """Update conversation, handling participants separately."""
        participants_ids = validated_data.pop('participants_ids', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update participants if provided
        if participants_ids is not None:
            participants = User.objects.filter(user_id__in=participants_ids)
            instance.participants.set(participants)
        
        return instance


class ConversationSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Conversation model.
    Used in listings without full message history.
    """
    participants = UserSummarySerializer(many=True, read_only=True)
    participants_count = serializers.ReadOnlyField(source='get_participants_count')
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participants_count',
            'last_message',
            'unread_count',
            'created_at',
            'last_message_at',
            'is_active',
        ]
        read_only_fields = ['conversation_id', 'created_at', 'last_message_at']
    
    def get_last_message(self, obj):
        """Get the most recent message in the conversation."""
        last_message = obj.messages.filter(is_deleted=False).order_by('-sent_at').first()
        if last_message:
            return MessageSummarySerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        """Get count of unread messages for the requesting user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False,
                is_deleted=False
            ).exclude(sender=request.user).count()
        return 0


# Authentication Serializers
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Try to authenticate with email as username
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
