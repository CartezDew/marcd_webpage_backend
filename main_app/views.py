from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, permissions


from .models import (
    ContactUs
)
from .serializers import (
    ContactUsSerializer
)


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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ['id', 'contact_id', 'first_name', 'last_name', 'email', 'feedback_type', 'message']


class ContactUsViewSet(viewsets.ModelViewSet):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    authentication_classes = [TokenAuthentication]
    lookup_field = 'contact_id'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]



