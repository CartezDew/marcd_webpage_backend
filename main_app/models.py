from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
import re
import os
import uuid


class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'parent']
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name}/{self.name}"
        return self.name
    
    def get_full_path(self):
        """Get the full path of the folder including all parent folders"""
        path_parts = [self.name]
        current = self.parent
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        return '/'.join(path_parts)
    
    def get_children_folders(self):
        """Get all direct child folders"""
        return self.children.all()
    
    def get_children_files(self):
        """Get all direct child files"""
        return self.files.all()
    
    def is_descendant_of(self, folder):
        """Check if this folder is a descendant of the given folder"""
        current = self.parent
        while current:
            if current == folder:
                return True
            current = current.parent
        return False


class FileTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(default=0)  # Size in bytes
    file_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(FileTag, blank=True, related_name='files')
    is_public = models.BooleanField(default=False)
    search_vector = SearchVectorField(null=True, blank=True)
    
    class Meta:
        unique_together = ['name', 'folder']
        ordering = ['name']
        indexes = [
            GinIndex(fields=['search_vector'])
        ]
    
    def __str__(self):
        if self.folder:
            return f"{self.folder.name}/{self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        # Set file size and type before saving
        if self.file:
            try:
                # Always update file type from the filename
                self.file_type = os.path.splitext(self.file.name)[1].lower()
                
                # Try to get file size - this should work for newly uploaded files
                if hasattr(self.file, 'size'):
                    self.file_size = self.file.size
                # Fallback: check if file exists in storage
                elif hasattr(self.file, 'storage') and self.file.storage.exists(self.file.name):
                    self.file_size = self.file.size
            except (OSError, IOError, AttributeError):
                # If file doesn't exist or can't be accessed, keep the existing file_size
                pass
        super().save(*args, **kwargs)
    
    def get_full_path(self):
        """Get the full path of the file including folder structure"""
        if self.folder:
            return f"{self.folder.get_full_path()}/{self.name}"
        return self.name
    
    def get_file_size_display(self):
        """Get human readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_latest_version(self):
        """Get the latest version of this file"""
        return self.versions.order_by('-version_number').first()
    
    def get_version_count(self):
        """Get the number of versions for this file"""
        return self.versions.count()


class FileVersion(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    version_file = models.FileField(upload_to='uploads/versions/')
    file_size = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    change_description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['file', 'version_number']
        ordering = ['-version_number']
    
    def __str__(self):
        return f"{self.file.name} v{self.version_number}"
    
    def save(self, *args, **kwargs):
        if self.version_file:
            self.file_size = self.version_file.size
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Get human readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FilePermission(models.Model):
    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('admin', 'Admin'),
    ]
    
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='read')
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['file', 'user']
        ordering = ['-granted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.permission_type} on {self.file.name}"
    
    def is_expired(self):
        """Check if the permission has expired"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False


class FilePreview(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='preview')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    preview_data = models.JSONField(null=True, blank=True)  # For text previews
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Preview for {self.file.name}"


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
