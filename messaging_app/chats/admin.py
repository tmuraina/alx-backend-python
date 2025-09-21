# chats/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface."""
    
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    readonly_fields = ('user_id', 'created_at', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation admin interface."""
    
    list_display = ('conversation_id', 'get_participants_list', 'created_at', 'last_message_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'last_message_at')
    search_fields = ('participants__email', 'participants__first_name', 'participants__last_name')
    readonly_fields = ('conversation_id', 'created_at')
    filter_horizontal = ('participants',)
    
    def get_participants_list(self, obj):
        return ", ".join([user.full_name for user in obj.participants.all()[:3]])
    get_participants_list.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin interface."""
    
    list_display = ('message_id', 'sender', 'conversation', 'message_preview', 'sent_at', 'is_read')
    list_filter = ('is_read', 'is_deleted', 'sent_at')
    search_fields = ('sender__email', 'sender__first_name', 'message_body')
    readonly_fields = ('message_id', 'sent_at')
    
    def message_preview(self, obj):
        return obj.message_body[:50] + "..." if len(obj.message_body) > 50 else obj.message_body
    message_preview.short_description = 'Message Preview'
