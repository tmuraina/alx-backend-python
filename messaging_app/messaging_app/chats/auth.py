# messaging_app/chats/auth.py

from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Simple custom token view for testing
    """
    pass
