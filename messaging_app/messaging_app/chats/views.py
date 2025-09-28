# messaging_app/chats/views.py

from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .permissions import IsParticipantInConversation, IsMessageSenderOrConversationParticipant

# Create your views here.
# You can add your ViewSets and API views here later 
