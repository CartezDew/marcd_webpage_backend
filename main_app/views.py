from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from .models import (
    ContactSubmission,
    TruckStop,
    WeatherData,
    TruckStopReview,
    UserFeedback
)
from .serializers import (
    ContactSubmissionSerializer,
    TruckStopSerializer,
    WeatherDataSerializer,
    TruckStopReviewSerializer,
    UserFeedbackSerializer
)


class Landing(APIView):
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


class TruckStopViewSet(viewsets.ModelViewSet):
    queryset = TruckStop.objects.all()
    serializer_class = TruckStopSerializer
    authentication_classes = []  # No authentication required
    permission_classes = [permissions.AllowAny]  # Public access

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
        except (TypeError, ValueError):
            return Response({"error": "Valid 'lat' and 'lng' query parameters are required."}, status=400)

        unit = request.query_params.get('unit', 'miles').lower()
        user_location = Point(lng, lat, srid=4326)

        queryset = TruckStop.objects.annotate(
            distance=Distance('location', user_location)
        ).order_by('distance')

        for stop in queryset:
            stop.distance_miles = round(stop.distance.mi, 2)
            stop.distance_km = round(stop.distance.km, 2)

        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request, 'user_location': user_location, 'unit': unit}
        )
        return Response(serializer.data)


class WeatherDataViewSet(viewsets.ModelViewSet):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    authentication_classes = []  # No authentication required
    permission_classes = [permissions.AllowAny]


class TruckStopReviewViewSet(viewsets.ModelViewSet):
    queryset = TruckStopReview.objects.all()
    serializer_class = TruckStopReviewSerializer
    authentication_classes = []  # No authentication required
    permission_classes = [permissions.AllowAny]


class UserFeedbackViewSet(viewsets.ModelViewSet):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    authentication_classes = []  # No authentication required

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
