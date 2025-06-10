from django.urls import path
from .views import (
    Landing,
    FeaturesView,
    ContactView,
    SurveyView,
    survey_form_view,
    SurveySuccessView,
    ContactListView,
)

urlpatterns = [
    path('', Landing.as_view(), name='landing'),
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('contact/list/', ContactListView.as_view(), name='contact-list'),
    path('api/survey/', SurveyView.as_view(), name='survey-api'),
    path('survey/', SurveyView.as_view(), name='survey'),
    path('survey/success/', SurveySuccessView.as_view(), name='survey-success'),
]
