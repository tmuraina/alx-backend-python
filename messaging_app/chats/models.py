# messaging_app/chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds additional fields like user_id, phone_number, and role.
    """
    
    # Role choices
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    # Primary key as UUID
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Override first_name and last_name to make them required
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    
    # Email field (already exists in AbstractUser, but ensure it's unique and required)
    email = models.EmailField(unique=True, null=False, blank=False)
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        null=True,
        blank=True,
        help_text="Phone number in international format"
    )
    
    # Role field
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='guest',
        null=False,
        blank=False
    )
    
    # Timestamp for when user was created (AbstractUser has date_joined, but we'll add created_at for consistency)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Use email as the username field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'chats_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_user_email'),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}"


class Conversation(models.Model):
    """
    Model representing a conversation between multiple users.
    Uses a many-to-many relationship to track participants.
    """
    
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Many-to-many relationship with User for participants
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        blank=False,
        help_text="Users participating in this conversation"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Additional fields for better conversation management
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chats_conversation'
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['last_message_at']),
        ]
        ordering = ['-last_message_at', '-created_at']
    
    def __str__(self):
        participants_names = ", ".join([user.full_name for user in self.participants.all()[:3]])
        if self.participants.count() > 3:
            participants_names += f" and {self.participants.count() - 3} others"
        return f"Conversation: {participants_names}"
    
    def get_participants_count(self):
        """Returns the number of participants in the conversation."""
        return self.participants.count()
    
    def add_participant(self, user):
        """Add a user to the conversation."""
        self.participants.add(user)
    
    def remove_participant(self, user):
        """Remove a user from the conversation."""
        self.participants.remove(user)


class Message(models.Model):
    """
    Model representing a message in a conversation.
    Links to a sender (User) and a conversation.
    """
    
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Foreign key to User (sender)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=False,
        help_text="User who sent this message"
    )
    
    # Foreign key to Conversation
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        null=False,
        help_text="Conversation this message belongs to"
    )
    
    # Message content
    message_body = models.TextField(
        null=False,
        blank=False,
        help_text="The content of the message"
    )
    
    # Timestamp
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Additional fields for message management
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chats_message'
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['sent_at']),
            models.Index(fields=['is_read']),
        ]
        ordering = ['-sent_at']
        constraints = [
            # Ensure sender is a participant in the conversation
            models.CheckConstraint(
                check=models.Q(message_body__isnull=False),
                name='message_body_not_null'
            ),
        ]
    
    def __str__(self):
        preview = self.message_body[:50] + "..." if len(self.message_body) > 50 else self.message_body
        return f"Message by {self.sender.full_name}: {preview}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to update conversation's last_message_at timestamp.
        """
        super().save(*args, **kwargs)
        
        # Update the conversation's last_message_at timestamp
        if self.conversation:
            self.conversation.last_message_at = self.sent_at
            self.conversation.save(update_fields=['last_message_at'])
    
    def mark_as_read(self):
        """Mark the message as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
    
    def soft_delete(self):
        """Soft delete the message (mark as deleted instead of removing from DB)."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])


# Optional: Manager classes for custom querysets
class MessageManager(models.Manager):
    """Custom manager for Message model."""
    
    def active_messages(self):
        """Return only non-deleted messages."""
        return self.filter(is_deleted=False)
    
    def unread_messages(self):
        """Return only unread messages."""
        return self.filter(is_read=False, is_deleted=False)
    
    def messages_for_user(self, user):
        """Return messages for conversations where user is a participant."""
        return self.filter(
            conversation__participants=user,
            is_deleted=False
        ).distinct()


class ConversationManager(models.Manager):
    """Custom manager for Conversation model."""
    
    def active_conversations(self):
        """Return only active conversations."""
        return self.filter(is_active=True)
    
    def conversations_for_user(self, user):
        """Return conversations where user is a participant."""
        return self.filter(participants=user, is_active=True).distinct()


# Add the custom managers to the models
Message.add_to_class('objects', MessageManager())
Conversation.add_to_class('objects', ConversationManager())
