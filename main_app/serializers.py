from rest_framework import serializers
from .models import ContactSubmission, SurveyResponse

class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ['first_name', 'last_name', 'email', 'message', 'submitted_at']

class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = ['first_name', 'last_name', 'email', 'experience', 'feedback', 'submitted_at']
