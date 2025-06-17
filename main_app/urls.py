from django.urls import path
from .views import (
    Landing,
    FeaturesView,
    ContactView,
    ContactListView,
    TruckStopViewSet,
    WeatherDataViewSet,
    TruckStopReviewViewSet,
    UserFeedbackViewSet,
)

urlpatterns = [
    path('', Landing.as_view(), name='landing'),
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('contact/list/', ContactListView.as_view(), name='contact-list'),
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
    path('feedback/', UserFeedbackViewSet.as_view({'get': 'list', 'post': 'create'}), name='feedback-list'),
    path('feedback/<int:pk>/', UserFeedbackViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='feedback-detail'),
]
