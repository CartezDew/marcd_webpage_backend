from rest_framework import serializers
from .models import ContactSubmission, TruckStop, WeatherData, TruckStopReview, UserFeedback

class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = '__all__'

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

class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = '__all__'


