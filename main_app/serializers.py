from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Folder, File, FileTag, FileVersion, FilePermission, FilePreview, WaitlistEntry, ContactSubmission, ContactUs, UserSecurityQuestions
import re


class UserSecurityQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSecurityQuestions
        fields = ['security_answer', 'professor_last_name']
        extra_kwargs = {
            'security_answer': {'write_only': True},
            'professor_last_name': {'write_only': True}
        }


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    security_answer = serializers.CharField(required=True)
    professor_last_name = serializers.CharField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    security_answer = serializers.CharField(required=True)
    professor_last_name = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value


class SecurityQuestionsSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSecurityQuestions
        fields = ['security_answer', 'professor_last_name']
        extra_kwargs = {
            'security_answer': {'write_only': True},
            'professor_last_name': {'write_only': True}
        }


class EmailPasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailPasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)


class EmailPasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value


class FileTagSerializer(serializers.ModelSerializer):
    files_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FileTag
        fields = ['id', 'name', 'color', 'files_count', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_files_count(self, obj):
        return obj.files.count()


class FileVersionSerializer(serializers.ModelSerializer):
    file_size_display = serializers.ReadOnlyField(source='get_file_size_display')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = FileVersion
        fields = ['id', 'file', 'version_number', 'version_file', 'file_size', 'file_size_display', 'created_at', 'created_by', 'created_by_username', 'change_description']
        read_only_fields = ['id', 'file_size', 'created_at', 'created_by']


class FilePermissionSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    granted_by_username = serializers.ReadOnlyField(source='granted_by.username')
    is_expired = serializers.ReadOnlyField(source='is_expired')
    
    class Meta:
        model = FilePermission
        fields = ['id', 'file', 'user', 'user_username', 'permission_type', 'granted_by', 'granted_by_username', 'granted_at', 'expires_at', 'is_expired']
        read_only_fields = ['id', 'granted_by', 'granted_at']


class FilePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilePreview
        fields = ['id', 'file', 'thumbnail', 'preview_data', 'generated_at']
        read_only_fields = ['id', 'generated_at']


class FolderSerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField(source='get_full_path')
    children_count = serializers.SerializerMethodField()
    files_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent', 'description', 'full_path', 'children_count', 'files_count', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.children.count()
    
    def get_files_count(self, obj):
        return obj.files.count()
    
    def validate_name(self, value):
        # Check for invalid characters in folder name
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in value:
                raise serializers.ValidationError(f"Folder name cannot contain: {char}")
        
        # Check for reserved names
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if value.upper() in reserved_names:
            raise serializers.ValidationError(f"'{value}' is a reserved name and cannot be used")
        
        return value


class FileSerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField(source='get_full_path')
    file_size_display = serializers.ReadOnlyField(source='get_file_size_display')
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')
    tags = FileTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True, 
        queryset=FileTag.objects.all(), 
        required=False,
        source='tags'
    )
    version_count = serializers.ReadOnlyField(source='get_version_count')
    latest_version = serializers.ReadOnlyField(source='get_latest_version.version_number')
    
    class Meta:
        model = File
        fields = [
            'id', 'name', 'file', 'folder', 'full_path', 'file_size', 'file_size_display', 
            'file_type', 'uploaded_by', 'uploaded_by_username', 'uploaded_at', 'description',
            'tags', 'tag_ids', 'is_public', 'version_count', 'latest_version'
        ]
        read_only_fields = ['id', 'file_size', 'file_type', 'uploaded_by', 'uploaded_at', 'version_count', 'latest_version']
    
    def validate_name(self, value):
        # Check for invalid characters in file name
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in value:
                raise serializers.ValidationError(f"File name cannot contain: {char}")
        
        # Check for reserved names
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if value.upper() in reserved_names:
            raise serializers.ValidationError(f"'{value}' is a reserved name and cannot be used")
        
        return value


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
        read_only_fields = ['id', 'contact_id', 'created_at']

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
        # Only validate required fields if they are being updated
        # For partial updates (like updating is_read), skip required field validation
        if self.partial:
            return data
            
        # Ensure required fields are present for full updates
        if not data.get('first_name'):
            raise serializers.ValidationError("First name is required")
        if not data.get('last_name'):
            raise serializers.ValidationError("Last name is required")
        if not data.get('email'):
            raise serializers.ValidationError("Email is required")
        if not data.get('message'):
            raise serializers.ValidationError("Message is required")
        return data




