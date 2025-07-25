from rest_framework import serializers
from .models import ContactUs, WaitlistEntry
import re


class WaitlistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistEntry
        fields = ['id', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_email(self, value):
        # Check if email contains @ symbol
        if '@' not in value:
            raise serializers.ValidationError("Email must contain @ symbol")
        
        # Check if email contains . symbol
        if '.' not in value:
            raise serializers.ValidationError("Email must contain a domain (e.g., .com, .org)")
        
        # Check if email is 'noemail' or contains 'noemail'
        if value.lower() == 'noemail' or 'noemail' in value.lower():
            raise serializers.ValidationError("Please enter a valid email address")
        
        # Basic email format validation
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
            raise serializers.ValidationError("Please enter a valid email address format")
        
        # Check for duplicate email (case-insensitive)
        if WaitlistEntry.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Invalid email address, please try again.")
        
        return value


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
        # Check if email contains @ symbol
        if '@' not in value:
            raise serializers.ValidationError("Email must contain @ symbol")
        
        # Check if email contains . symbol
        if '.' not in value:
            raise serializers.ValidationError("Email must contain a domain (e.g., .com, .org)")
        
        # Check if email is 'noemail' or contains 'noemail'
        if value.lower() == 'noemail' or 'noemail' in value.lower():
            raise serializers.ValidationError("Please enter a valid email address")
        
        # Basic email format validation
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
            raise serializers.ValidationError("Please enter a valid email address format")
        
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




