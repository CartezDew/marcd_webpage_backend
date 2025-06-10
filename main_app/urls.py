from django.urls import path
from .views import (
    Landing,
    FeaturesView,
    ContactView,
    ContactListView,
)

urlpatterns = [
    path('', Landing.as_view(), name='landing'),
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('contact/list/', ContactListView.as_view(), name='contact-list'),
]
