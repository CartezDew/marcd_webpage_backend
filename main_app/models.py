from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


class ContactSubmission(models.Model):
    contact_id = models.CharField(max_length=10, unique=True, editable=False, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.contact_id:
            last_contact = ContactSubmission.objects.order_by('-id').first()
            if last_contact and last_contact.contact_id:
                last_id_num = int(last_contact.contact_id.replace("CT-", ""))
                new_id_num = last_id_num + 1
            else:
                new_id_num = 1
            self.contact_id = f"CT-{new_id_num:03d}"  # CT-001, CT-002, etc.
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contact_id} - {self.first_name} {self.last_name}"

class TruckStop(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = gis_models.PointField(geography=True, null=True, blank=True)  # NEW FIELD
    parking_spaces = models.IntegerField()
    available_spaces = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    # objects = GeoManager() # this line enables .annotate(Distance(...)) for spatial features

    def save(self, *args, **kwargs):
        # Automatically set location from lat/lng
        if self.latitude and self.longitude:
            self.location = gis_models.Point(self.longitude, self.latitude)
        super().save(*args, **kwargs)
    
    # Amenities
    has_showers = models.BooleanField(default=False)
    has_restaurant = models.BooleanField(default=False)
    has_repair_shop = models.BooleanField(default=False)
    has_fuel = models.BooleanField(default=False)
    
    # Ratings (averages)
    cleanliness_rating = models.FloatField(default=0)
    food_rating = models.FloatField(default=0)
    safety_rating = models.FloatField(default=0)

    def __str__(self):
        return self.name

class WeatherData(models.Model):
    truck_stop = models.ForeignKey(TruckStop, on_delete=models.CASCADE, related_name='weather_data')
    temperature = models.FloatField()
    conditions = models.CharField(max_length=100)
    wind_speed = models.FloatField()
    precipitation = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather at {self.truck_stop.name} - {self.timestamp}"

class TruckStopReview(models.Model):
    truck_stop = models.ForeignKey(TruckStop, on_delete=models.CASCADE, related_name='reviews')
    cleanliness_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    food_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    safety_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    parking_availability = models.CharField(
        max_length=20,
        choices=[('full', 'Full'), ('limited', 'Limited'), ('available', 'Available')]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.truck_stop.name} - {self.created_at}"

class ContactUs(models.Model):
    contact_id = models.CharField(max_length=10, unique=True, editable=False, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    social_media = models.CharField(max_length=100, blank=True)
    phone = models.CharField(
        max_length=12, 
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}-\d{3}-\d{4}$',
                message='Phone number must be in format: XXX-XXX-XXXX'
            )
        ]
    )
    feedback_type = models.CharField(
        max_length=50,
        choices=[
            ('general', 'General Inquiry'),
            ('bug', 'Bug Report'),
            ('feature', 'Feature Request'),
            ('other', 'Other')
        ],
        default='general'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.contact_id:
            last_contact = ContactUs.objects.order_by('-id').first()
            if last_contact and last_contact.contact_id:
                last_id_num = int(last_contact.contact_id.replace("CT-", ""))
                new_id_num = last_id_num + 1
            else:
                new_id_num = 1
            self.contact_id = f"CT-{new_id_num:03d}"  # CT-001, CT-002, etc.
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # Validate email contains @ symbol
        if self.email and '@' not in self.email:
            raise ValidationError({'email': 'Email must contain @ symbol'})

    def __str__(self):
        return f"{self.contact_id} - {self.first_name} {self.last_name} - {self.feedback_type}"
