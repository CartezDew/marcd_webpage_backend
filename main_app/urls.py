from django.urls import path
from .views import (
    Landing,
    FeaturesView,
    ContactView,
    ContactUsViewSet,
    WaitlistView,
    WaitlistListView,
    WaitlistEntryViewSet,
)

urlpatterns = [
    path('', Landing.as_view(), name='landing'),
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('waitlist/', WaitlistView.as_view(), name='waitlist'),
    path('waitlist/list/', WaitlistListView.as_view(), name='waitlist-list'),
    path('waitlist-entries/', WaitlistEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='waitlist-entries-list'),
    path('waitlist-entries/<int:id>/', WaitlistEntryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='waitlist-entries-detail'),
    path('contactus/', ContactUsViewSet.as_view({'get': 'list', 'post': 'create'}), name='contactus-list'),
    path('contactus/<str:contact_id>/', ContactUsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='contactus-detail'),
  
]
