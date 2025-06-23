from django.urls import path
from .views import (
    Landing,
    FeaturesView,
    ContactView,
    ContactUsViewSet,
    TruckStopViewSet,
    WeatherDataViewSet,
    TruckStopReviewViewSet,
)

urlpatterns = [
    path('', Landing.as_view(), name='landing'),
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('contactus/', ContactUsViewSet.as_view({'get': 'list', 'post': 'create'}), name='contactus-list'),
    path('contactus/<str:contact_id>/', ContactUsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='contactus-detail'),
    path('truck-stops/', TruckStopViewSet.as_view({'get': 'list', 'post': 'create'}), name='truck-stop-list'),
    path('truck-stops/<int:pk>/', TruckStopViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='truck-stop-detail'),
    path('truck-stops/nearby/', TruckStopViewSet.as_view({'get': 'nearby'}), name='truck-stop-nearby'),
    path('weather/', WeatherDataViewSet.as_view({'get': 'list', 'post': 'create'}), name='weather-list'),
    path('weather/<int:pk>/', WeatherDataViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='weather-detail'),
    path('reviews/', TruckStopReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='review-list'),
    path('reviews/<int:pk>/', TruckStopReviewViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='review-detail'),
]
