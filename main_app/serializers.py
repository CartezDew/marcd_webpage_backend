from rest_framework import serializers
from .models import TruckStop, WeatherData, TruckStopReview, ContactUs
import re



class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['contact_id', 'first_name', 'last_name', 'email', 'social_media', 'phone', 'feedback_type', 'message', 'created_at', 'is_read']
        read_only_fields = ['contact_id', 'created_at', 'is_read']

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

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'

class TruckStopReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckStopReview
        fields = '__all__'

class TruckStopSerializer(serializers.ModelSerializer):
    weather_data = WeatherDataSerializer(many=True, read_only=True)
    reviews = TruckStopReviewSerializer(many=True, read_only=True)
    distance = serializers.SerializerMethodField()

    class Meta:
        model = TruckStop
        fields = '__all__'  # or list fields explicitly
        read_only_fields = ['distance']

    def get_distance(self, obj):
        unit = self.context.get('unit', 'miles')
        if hasattr(obj, 'distance') and obj.distance:
            if unit == 'km':
                return {'distance_km': round(obj.distance.km, 2)}
            else:
                return {'distance_miles': round(obj.distance.mi, 2)}
        return None


