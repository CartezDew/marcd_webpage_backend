from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


from .models import (
    ContactUs,
    WaitlistEntry
)
from .serializers import (
    ContactUsSerializer,
    WaitlistEntrySerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that accepts either username or email
    """
    def post(self, request, *args, **kwargs):
        username_or_email = request.data.get('username', '')
        password = request.data.get('password', '')
        
        if not username_or_email or not password:
            return Response({
                'error': 'Both username/email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to authenticate with username first
        user = authenticate(username=username_or_email, password=password)
        
        # If that fails, try to find user by email and authenticate
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
            except User.MultipleObjectsReturned:
                # If multiple users have the same email, try the first one
                try:
                    user_obj = User.objects.filter(email=username_or_email).first()
                    if user_obj:
                        user = authenticate(username=user_obj.username, password=password)
                except:
                    user = None
        
        if user is None:
            return Response({
                'error': 'Invalid credentials. Please check your username/email and password.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Account is disabled.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        return Response({
            'refresh': str(refresh),
            'access': str(access),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        }, status=status.HTTP_200_OK)


class Landing(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({"message": "Welcome to the Marc'd API landing route!"})


class FeaturesView(APIView):
    def get(self, request):
        return Response({
            "features": [
                {"title": "GPS Truck Stop Finder", "description": "Find truck stops near your location in real time."},
                {"title": "Weather Updates", "description": "See local weather conditions on the road."},
                {"title": "Parking Availability", "description": "Get real-time parking availability from other drivers."},
                {"title": "Cleanliness & Food Reviews", "description": "Know what to expect before stopping."},
            ]
        })


class WaitlistView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = [permissions.AllowAny]  # Public access
    
    def post(self, request):
        serializer = WaitlistEntrySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    "message": "Successfully added to waitlist!",
                    "email": serializer.data['email']
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Failed to add to waitlist. Please try again."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaitlistListView(ListAPIView):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntrySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ['email', 'created_at']


class WaitlistEntryViewSet(viewsets.ModelViewSet):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntrySerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ContactView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = [permissions.AllowAny]  # Public access
    
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Thanks for reaching out!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactListView(ListAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ['id', 'contact_id', 'first_name', 'last_name', 'email', 'feedback_type', 'message']


class ContactUsViewSet(viewsets.ModelViewSet):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    lookup_field = 'contact_id'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]



