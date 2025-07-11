from django.urls import path
from .views import (
    Landing,
    FeaturesView,
    ContactView,
    ContactUsViewSet,
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
  
]
