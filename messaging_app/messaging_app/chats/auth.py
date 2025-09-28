# messaging_app/chats/auth.py

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to include additional user information in the token
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra responses here
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that returns JWT tokens with user information
    """
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return JWT tokens
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return Response({
                    'error': f'{field} is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        username = data['username']
        email = data['email']
        password = data['password']
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return Response({
                'error': 'Invalid email format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        if len(password) < 8:
            return Response({
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
        except IntegrityError:
            return Response({
                'error': 'User creation failed. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Add custom claims
        access_token['username'] = user.username
        access_token['email'] = user.email
        access_token['first_name'] = user.first_name
        access_token['last_name'] = user.last_name
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Registration failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user and return JWT tokens
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Add custom claims
                access_token['username'] = user.username
                access_token['email'] = user.email
                access_token['first_name'] = user.first_name
                access_token['last_name'] = user.last_name
                
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Account is disabled'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'error': 'Login failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def logout_user(request):
    """
    Logout user by blacklisting the refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile(request):
    """
    Get current user profile information
    """
    try:
        user = request.user
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
