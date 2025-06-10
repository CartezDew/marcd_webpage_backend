from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from .models import ContactSubmission
from rest_framework.permissions import IsAdminUser
from .serializers import ContactSubmissionSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter


from django.views.generic import TemplateView
from django.shortcuts import render, redirect


class Landing(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the Marc’d API landing route!"})


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
    def post(self, request):
        serializer = ContactSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Thanks for reaching out!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactListView(ListAPIView):
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']

