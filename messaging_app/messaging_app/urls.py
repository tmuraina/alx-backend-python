# messaging_app/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from chats.auth import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('api/auth/', include([
        path('register/', include('chats.urls')),  # Will include register endpoint
        path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        path('', include('chats.urls')),  # Include all other auth endpoints
    ])),
    
    # Main app URLs
    path('api/', include('chats.urls')),
]
