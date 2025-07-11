from rest_framework import serializers
from .models import ContactUs
import re



class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'contact_id', 'first_name', 'last_name', 'email', 'social_media', 'phone', 'feedback_type', 'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'contact_id', 'created_at', 'is_read']

    def validate_phone(self, value):
        if value:
            # Check if phone number matches XXX-XXX-XXXX format
            if not re.match(r'^\d{3}-\d{3}-\d{4}$', value):
                raise serializers.ValidationError("Phone number must be in format: XXX-XXX-XXXX")
        return value

    def validate_email(self, value):
        if '@' not in value:
            raise serializers.ValidationError("Email must contain @ symbol")
        return value

    def validate(self, data):
        # Ensure required fields are present
        if not data.get('first_name'):
            raise serializers.ValidationError("First name is required")
        if not data.get('last_name'):
            raise serializers.ValidationError("Last name is required")
        if not data.get('email'):
            raise serializers.ValidationError("Email is required")
        if not data.get('message'):
            raise serializers.ValidationError("Message is required")
        return data




