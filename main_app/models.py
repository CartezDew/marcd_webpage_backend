from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


class WaitlistEntry(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        super().clean()
        # Validate email contains @ symbol
        if self.email and '@' not in self.email:
            raise ValidationError({'email': 'Email must contain @ symbol'})
        
        # Validate email contains . symbol
        if self.email and '.' not in self.email:
            raise ValidationError({'email': 'Email must contain a domain (e.g., .com, .org)'})
        
        # Validate email is not 'noemail' or contains 'noemail'
        if self.email and ('noemail' in self.email.lower()):
            raise ValidationError({'email': 'Please enter a valid email address'})
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.email} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    class Meta:
        verbose_name_plural = "Waitlist Entries"
        ordering = ['-created_at']


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
        
        # Validate email contains . symbol
        if self.email and '.' not in self.email:
            raise ValidationError({'email': 'Email must contain a domain (e.g., .com, .org)'})
        
        # Validate email is not 'noemail' or contains 'noemail'
        if self.email and ('noemail' in self.email.lower()):
            raise ValidationError({'email': 'Please enter a valid email address'})
        
        # Basic email format validation
        if self.email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', self.email):
            raise ValidationError({'email': 'Please enter a valid email address format'})

    def __str__(self):
        return f"{self.contact_id} - {self.first_name} {self.last_name} - {self.feedback_type}"
