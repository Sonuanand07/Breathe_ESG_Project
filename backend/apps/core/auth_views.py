"""
Authentication views for Breathe ESG API.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint that validates credentials and returns auth token.
    
    Expected request body:
    {
        "email": "analyst@breatheesg.com",
        "password": "demo1234"
    }
    
    Returns:
    {
        "token": "abc123...",
        "user": {
            "id": 1,
            "email": "analyst@breatheesg.com",
            "name": "Demo Analyst"
        }
    }
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Simple demo authentication - in production, validate against real credentials
    if email == 'analyst@breatheesg.com' and password == 'demo1234':
        # Get or create user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': 'Demo',
                'last_name': 'Analyst'
            }
        )
        
        # Get or create token
        token, _ = Token.objects.get_or_create(user=user)
        
        logger.info(f"User {email} logged in successfully")
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.get_full_name() or user.username
            }
        }, status=status.HTTP_200_OK)
    else:
        logger.warning(f"Failed login attempt for email: {email}")
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def logout(request):
    """
    Logout endpoint that invalidates the user's token.
    """
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
