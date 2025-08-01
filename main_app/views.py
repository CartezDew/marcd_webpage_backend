from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import os
import mimetypes
import zipfile
import tempfile
from django.http import FileResponse


def rate_limit(key_prefix, limit=100, period=3600):
    """
    Rate limiting decorator
    key_prefix: prefix for cache key
    limit: maximum requests per period
    period: time period in seconds
    """
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            # Create cache key based on user and action
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            cache_key = f"{key_prefix}:{user_id}"
            
            # Get current count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit:
                return Response(
                    {'error': 'Rate limit exceeded. Please try again later.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Increment count
            cache.set(cache_key, current_count + 1, period)
            
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


from .models import (
    ContactUs,
    WaitlistEntry,
    File,
    Folder,
    FileTag,
    FileVersion,
    FilePermission,
    FilePreview,
    UserSecurityQuestions,
    PasswordResetCode,
    AdminLoginLog
)
from .serializers import (
    ContactUsSerializer,
    WaitlistEntrySerializer,
    FileSerializer,
    FolderSerializer,
    FileTagSerializer,
    FileVersionSerializer,
    FilePermissionSerializer,
    FilePreviewSerializer,
    UserSecurityQuestionsSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailPasswordResetRequestSerializer,
    EmailPasswordResetVerifySerializer,
    EmailPasswordResetConfirmSerializer
)
import json
import os
import zipfile
import tempfile
import mimetypes
from functools import wraps
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(APIView):
    """
    Custom JWT login view that accepts either username or email
    Handles multiple field names for better frontend compatibility
    """
    authentication_classes = []
    permission_classes = []
    
    def log_mobile_request(self, request, success=True, error_msg=None):
        """Log mobile requests for debugging"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_mobile = any(indicator in user_agent.lower() for indicator in ['mobile', 'android', 'iphone', 'ipad'])
        
        if is_mobile:
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'method': request.method,
                'path': request.path,
                'user_agent': user_agent,
                'ip': request.META.get('REMOTE_ADDR', ''),
                'success': success,
                'error': error_msg,
                'data': request.data if hasattr(request, 'data') else None,
            }
            print(f"MOBILE_LOGIN_DEBUG: {log_data}")
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            # Log mobile request at start
            self.log_mobile_request(request, success=False, error_msg="Request started")
            
            # Parse request data from multiple sources
            data = {}
            
            # Try request.data first (DRF parsed data)
            if hasattr(request, 'data') and request.data:
                data = request.data
            # Fallback to request.POST for form data
            elif hasattr(request, 'POST') and request.POST:
                data = request.POST
            # Last resort: parse JSON from request.body
            else:
                try:
                    import json
                    if hasattr(request, 'body') and request.body:
                        data = json.loads(request.body.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    data = {}
            
            # Handle multiple possible field names for username/email
            username_or_email = (
                data.get('username') or 
                data.get('email') or 
                data.get('user') or 
                data.get('login') or
                data.get('identifier') or
                ''
            )
            password = data.get('password', '')
            
            # Log the request data for debugging
            if settings.DEBUG:
                print(f"CustomTokenObtainPairView - Login attempt")
                print(f"Request method: {request.method}")
                print(f"Content type: {request.content_type}")
                print(f"Data keys: {list(data.keys()) if data else 'No data'}")
                print(f"Username/Email extracted: '{username_or_email}'")
                print(f"Password provided: {'Yes' if password else 'No'}")
            
            if not username_or_email or not password:
                self.log_mobile_request(request, success=False, error_msg="Missing credentials")
                return Response({
                    'error': 'Both username/email and password are required',
                    'received_data': list(data.keys()) if settings.DEBUG and data else None,
                    'debug_info': {
                        'content_type': request.content_type,
                        'method': request.method,
                        'has_data': bool(data)
                    } if settings.DEBUG else None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Try to authenticate with username first
            user = authenticate(username=username_or_email, password=password)
            
            # If that fails, try to find user by email and authenticate
            if user is None:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
                except User.MultipleObjectsReturned:
                    # If multiple users have the same email, try the first one
                    try:
                        user_obj = User.objects.filter(email=username_or_email).first()
                        if user_obj:
                            user = authenticate(username=user_obj.username, password=password)
                    except:
                        user = None
            
            if user is None:
                self.log_mobile_request(request, success=False, error_msg="Invalid credentials")
                return Response({
                    'error': 'Invalid credentials. Please check your username/email and password.',
                    'hint': 'Make sure you are using the correct username/email and password combination.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                self.log_mobile_request(request, success=False, error_msg="Account disabled")
                return Response({
                    'error': 'Account is disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Log successful login
            self.log_mobile_request(request, success=True, error_msg=None)
            
            return Response({
                'refresh': str(refresh),
                'access': str(access),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log the full error for debugging
            self.log_mobile_request(request, success=False, error_msg=f"Exception: {str(e)}")
            if settings.DEBUG:
                print(f"CustomTokenObtainPairView error: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
            
            return Response({
                'error': 'An unexpected error occurred during authentication.',
                'detail': str(e) if settings.DEBUG else 'Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class MobileLoginTestView(APIView):
    """
    Debug view to test mobile login requests
    """
    authentication_classes = []
    permission_classes = []
    
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return Response({
            'message': 'Test endpoint reached successfully',
            'method': request.method,
            'content_type': request.content_type,
            'headers': dict(request.headers),
            'data': request.data if hasattr(request, 'data') else None,
            'post': dict(request.POST) if hasattr(request, 'POST') else None,
            'body': request.body.decode('utf-8') if hasattr(request, 'body') and request.body else None,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'remote_addr': request.META.get('REMOTE_ADDR', 'Unknown'),
        }, status=status.HTTP_200_OK)
    
    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Test GET endpoint works',
            'timestamp': str(timezone.now()) if hasattr(timezone, 'now') else 'timestamp unavailable'
        }, status=status.HTTP_200_OK)


class Landing(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({"message": "Welcome to the Marc'd API landing route!"})


class FeaturesView(APIView):
    def get(self, request):
        return Response({
            "features": [
                {"title": "GPS Truck Stop Finder", "description": "Find truck stops near your location in real time."},
                {"title": "Weather Updates", "description": "See local weather conditions on the road."},
                {"title": "Parking Availability", "description": "Get real-time parking availability from other drivers."},
                {"title": "Cleanliness & Food Reviews", "description": "Know what to expect before stopping."},
            ]
        })


class WaitlistView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = [permissions.AllowAny]  # Public access
    
    def post(self, request):
        serializer = WaitlistEntrySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    "message": "Successfully added to waitlist!",
                    "email": serializer.data['email']
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Failed to add to waitlist. Please try again."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaitlistListView(ListAPIView):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntrySerializer
    permission_classes = [IsAdminUser]
    # filter_backends = [SearchFilter]
    search_fields = ['email', 'created_at']


class WaitlistEntryViewSet(viewsets.ModelViewSet):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntrySerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ContactView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = [permissions.AllowAny]  # Public access
    
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Thanks for reaching out!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactListView(ListAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [IsAdminUser]
    # filter_backends = [SearchFilter]
    search_fields = ['id', 'contact_id', 'first_name', 'last_name', 'email', 'feedback_type', 'message']


class ContactUsViewSet(viewsets.ModelViewSet):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def partial_update(self, request, *args, **kwargs):
        """Custom partial_update method with debugging"""
        instance = self.get_object()
        print(f"Updating contact {instance.id} with data: {request.data}")
        print(f"Current is_read value: {instance.is_read}")
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            updated_instance = serializer.save()
            print(f"Updated is_read value: {updated_instance.is_read}")
            return Response(serializer.data)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    # filter_backends = [SearchFilter]
    search_fields = ['name', 'file_type', 'uploaded_by__username']
    lookup_field = 'pk'
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        queryset = File.objects.all()
        folder_id = self.request.query_params.get('folder', None)
        if folder_id:
            if folder_id == 'null':
                queryset = queryset.filter(folder__isnull=True)
            else:
                queryset = queryset.filter(folder_id=folder_id)
        return queryset
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests for updating file properties including moving files"""
        try:
            print(f"FileViewSet partial_update called with data: {request.data}")
            instance = self.get_object()
            print(f"File instance: {instance.name}, current folder: {instance.folder}")
            
            # Check if this is a move operation
            if 'folder' in request.data:
                target_folder_id = request.data.get('folder')
                print(f"Moving file to folder ID: {target_folder_id}")
                
                # Get target folder if specified
                target_folder = None
                if target_folder_id:
                    try:
                        target_folder = Folder.objects.get(id=target_folder_id)
                        print(f"Found target folder: {target_folder.name}")
                    except Folder.DoesNotExist:
                        print(f"Target folder {target_folder_id} not found")
                        return Response({'error': 'Target folder not found'}, status=status.HTTP_404_NOT_FOUND)
                
                # Check if file with same name exists in target folder
                if File.objects.filter(name=instance.name, folder=target_folder).exclude(id=instance.id).exists():
                    print(f"File with same name already exists in target folder")
                    return Response({'error': 'A file with this name already exists in the target folder'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Move file
                instance.folder = target_folder
                instance.save()
                print(f"File moved successfully to folder: {target_folder.name if target_folder else 'root'}")
                
                serializer = self.get_serializer(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Check if this is a rename operation
            if 'name' in request.data:
                new_name = request.data.get('name')
                print(f"Renaming file to: {new_name}")
                
                # Validate new name
                if not new_name or new_name.strip() == '':
                    return Response({'error': 'File name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if file with same name exists in the same folder
                if File.objects.filter(name=new_name, folder=instance.folder).exclude(id=instance.id).exists():
                    return Response({'error': 'A file with this name already exists in this folder'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Update name
                instance.name = new_name
                instance.save()
                
                serializer = self.get_serializer(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Handle other partial updates (description, tags, is_public, etc.)
            print(f"Handling other partial updates")
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Error in FileViewSet partial_update: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """Custom destroy method with better error handling"""
        try:
            instance = self.get_object()
            # Delete the file from storage
            if instance.file:
                try:
                    default_storage.delete(instance.file.name)
                except Exception:
                    pass  # Continue even if file deletion fails
            instance.delete()
            return Response({'message': 'File deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    # filter_backends = [SearchFilter]
    search_fields = ['name', 'created_by__username']
    lookup_field = 'pk'
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        queryset = Folder.objects.all()
        parent_id = self.request.query_params.get('parent', None)
        if parent_id:
            if parent_id == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        return queryset
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests for updating folder properties including renaming folders"""
        instance = self.get_object()
        
        # Check if this is a rename operation
        if 'name' in request.data:
            new_name = request.data.get('name')
            
            # Validate new name
            if not new_name or new_name.strip() == '':
                return Response({'error': 'Folder name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if folder with same name exists in the same parent
            if Folder.objects.filter(name=new_name, parent=instance.parent).exclude(id=instance.id).exists():
                return Response({'error': 'A folder with this name already exists in this location'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update name
            instance.name = new_name
            instance.save()
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Handle other partial updates (description, etc.)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Custom destroy method with better error handling"""
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'message': 'Folder deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_destroy(self, instance):
        """Recursively delete all contents of a folder, then the folder itself"""
        try:
            self._delete_folder_contents(instance)
            instance.delete()
        except Exception as e:
            # Log the error for debugging
            print(f"Error deleting folder {instance.id}: {str(e)}")
            raise ValidationError(f"The folder may contain files or there is a backend issue: {str(e)}")

    def _delete_folder_contents(self, folder):
        """Recursively delete all contents of a folder"""
        try:
            # Delete all files in this folder
            for file_obj in folder.files.all():
                try:
                    # Delete file versions
                    for version in file_obj.versions.all():
                        if version.version_file:
                            try:
                                default_storage.delete(version.version_file.name)
                            except Exception:
                                pass
                        version.delete()
                    
                    # Delete file permissions
                    file_obj.permissions.all().delete()
                    
                    # Delete file preview
                    try:
                        if hasattr(file_obj, 'preview') and file_obj.preview:
                            if file_obj.preview.thumbnail:
                                try:
                                    default_storage.delete(file_obj.preview.thumbnail.name)
                                except Exception:
                                    pass
                            file_obj.preview.delete()
                    except Exception:
                        pass
                    
                    # Delete the file itself
                    if file_obj.file:
                        try:
                            default_storage.delete(file_obj.file.name)
                        except Exception:
                            pass
                    file_obj.delete()
                except Exception as e:
                    print(f"Error deleting file {file_obj.id}: {str(e)}")
                    raise
            
            # Recursively delete all subfolders
            for subfolder in folder.children.all():
                try:
                    self._delete_folder_contents(subfolder)
                    subfolder.delete()
                except Exception as e:
                    print(f"Error deleting subfolder {subfolder.id}: {str(e)}")
                    raise
                    
        except Exception as e:
            print(f"Error in _delete_folder_contents for folder {folder.id}: {str(e)}")
            raise


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @rate_limit('file_upload', limit=50, period=3600)  # 50 uploads per hour
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('file')
            folder_id = request.data.get('folder')
            custom_name = request.data.get('name')
            # Handle boolean parameters that might come as strings
            replace_existing_raw = request.data.get('replace_existing', False)
            upload_as_duplicate_raw = request.data.get('upload_as_duplicate', False)
            overwrite_raw = request.data.get('overwrite', False)
            
            # Convert to boolean
            replace_existing = replace_existing_raw in [True, 'true', 'True', '1', 1]
            upload_as_duplicate = upload_as_duplicate_raw in [True, 'true', 'True', '1', 1]
            overwrite = overwrite_raw in [True, 'true', 'True', '1', 1]
            
            # If overwrite is true, treat it as replace_existing
            if overwrite:
                replace_existing = True
            
            # Debug logging
            print(f"DEBUG: Upload request received")
            print(f"DEBUG: folder_id = {folder_id} (type: {type(folder_id)})")
            print(f"DEBUG: replace_existing_raw = {replace_existing_raw} (type: {type(replace_existing_raw)})")
            print(f"DEBUG: replace_existing = {replace_existing}")
            print(f"DEBUG: upload_as_duplicate_raw = {upload_as_duplicate_raw} (type: {type(upload_as_duplicate_raw)})")
            print(f"DEBUG: upload_as_duplicate = {upload_as_duplicate}")
            print(f"DEBUG: overwrite_raw = {overwrite_raw} (type: {type(overwrite_raw)})")
            print(f"DEBUG: overwrite = {overwrite}")
            print(f"DEBUG: All request.data = {request.data}")
            
            if not uploaded_file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get folder if specified
            folder = None
            if folder_id:
                try:
                    folder = Folder.objects.get(id=folder_id)
                except Folder.DoesNotExist:
                    return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Use custom name if provided, otherwise use original filename
            file_name = custom_name if custom_name else uploaded_file.name
            
            # Check if file with same name exists in the specific folder
            existing_file = File.objects.filter(name=file_name, folder=folder).first()
            
            if existing_file:
                if replace_existing:
                    # Delete the existing file from storage
                    if existing_file.file and default_storage.exists(existing_file.file.name):
                        default_storage.delete(existing_file.file.name)
                    
                    # Update the existing file record
                    existing_file.file = uploaded_file
                    existing_file.file_size = uploaded_file.size
                    existing_file.file_type = os.path.splitext(uploaded_file.name)[1].lower()
                    existing_file.uploaded_by = request.user
                    existing_file.uploaded_at = timezone.now()
                    existing_file.save()
                    
                    serializer = FileSerializer(existing_file)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                    
                elif upload_as_duplicate:
                    # Generate a unique name with numbered suffix
                    base_name, extension = os.path.splitext(file_name)
                    counter = 1
                    new_name = f"{base_name} ({counter}){extension}"
                    
                    while File.objects.filter(name=new_name, folder=folder).exists():
                        counter += 1
                        new_name = f"{base_name} ({counter}){extension}"
                    
                    # Create new file object with the unique name
                    file_obj = File.objects.create(
                        name=new_name,
                        file=uploaded_file,
                        folder=folder,
                        uploaded_by=request.user
                    )
                    
                    serializer = FileSerializer(file_obj)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                    
                else:
                    # Return error with options
                    return Response({
                        'error': 'A file with this name already exists in this folder',
                        'options': {
                            'replace_existing': True,
                            'upload_as_duplicate': True
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create new file object (no conflict)
            file_obj = File.objects.create(
                name=file_name,
                file=uploaded_file,
                folder=folder,
                uploaded_by=request.user
            )
            
            serializer = FileSerializer(file_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    @rate_limit('file_download', limit=200, period=3600)  # 200 downloads per hour
    def get(self, request, pk):
        try:
            file_obj = get_object_or_404(File, id=pk)
            
            if not file_obj.file:
                return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if file exists on disk
            if not default_storage.exists(file_obj.file.name):
                return Response({'error': 'File not found on disk'}, status=status.HTTP_404_NOT_FOUND)
            
            # Open and read file
            with default_storage.open(file_obj.file.name, 'rb') as f:
                file_content = f.read()
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(file_obj.file.name)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create response
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileMoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            file_obj = get_object_or_404(File, id=pk)
            target_folder_id = request.data.get('target_folder')
            
            # Get target folder if specified
            target_folder = None
            if target_folder_id:
                try:
                    target_folder = Folder.objects.get(id=target_folder_id)
                except Folder.DoesNotExist:
                    return Response({'error': 'Target folder not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if file with same name exists in target folder
            if File.objects.filter(name=file_obj.name, folder=target_folder).exists():
                return Response({'error': 'A file with this name already exists in the target folder'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Move file
            file_obj.folder = target_folder
            file_obj.save()
            
            serializer = FileSerializer(file_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FolderMoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            folder_obj = get_object_or_404(Folder, id=pk)
            target_parent_id = request.data.get('target_parent')
            
            # Get target parent folder if specified
            target_parent = None
            if target_parent_id:
                try:
                    target_parent = Folder.objects.get(id=target_parent_id)
                    # Prevent moving folder into itself or its descendants
                    if target_parent == folder_obj or folder_obj.is_descendant_of(target_parent):
                        return Response({'error': 'Cannot move folder into itself or its descendants'}, status=status.HTTP_400_BAD_REQUEST)
                except Folder.DoesNotExist:
                    return Response({'error': 'Target parent folder not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if folder with same name exists in target parent
            if Folder.objects.filter(name=folder_obj.name, parent=target_parent).exists():
                return Response({'error': 'A folder with this name already exists in the target location'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Move folder
            folder_obj.parent = target_parent
            folder_obj.save()
            
            serializer = FolderSerializer(folder_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileTagViewSet(viewsets.ModelViewSet):
    queryset = FileTag.objects.all()
    serializer_class = FileTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [SearchFilter]
    search_fields = ['name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FileVersionViewSet(viewsets.ModelViewSet):
    queryset = FileVersion.objects.all()
    serializer_class = FileVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FilePermissionViewSet(viewsets.ModelViewSet):
    queryset = FilePermission.objects.all()
    serializer_class = FilePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(granted_by=self.request.user)


class FilePreviewViewSet(viewsets.ModelViewSet):
    queryset = FilePreview.objects.all()
    serializer_class = FilePreviewSerializer
    permission_classes = [permissions.IsAuthenticated]


class FileSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Full-text search using PostgreSQL
        search_vector = SearchVector('name', 'description')
        search_query = SearchQuery(query)
        
        files = File.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
        
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)


class FileVersionUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, file_id):
        try:
            file_obj = get_object_or_404(File, id=file_id)
            uploaded_file = request.FILES.get('file')
            change_description = request.data.get('change_description', '')
            
            if not uploaded_file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get next version number
            latest_version = file_obj.versions.order_by('-version_number').first()
            next_version = (latest_version.version_number + 1) if latest_version else 1
            
            # Create new version
            version = FileVersion.objects.create(
                file=file_obj,
                version_number=next_version,
                version_file=uploaded_file,
                created_by=request.user,
                change_description=change_description
            )
            
            serializer = FileVersionSerializer(version)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileVersionDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, file_id, version_number):
        try:
            version = get_object_or_404(FileVersion, file_id=file_id, version_number=version_number)
            
            if not version.version_file:
                return Response({'error': 'Version file not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if file exists on disk
            if not default_storage.exists(version.version_file.name):
                return Response({'error': 'Version file not found on disk'}, status=status.HTTP_404_NOT_FOUND)
            
            # Open and read file
            with default_storage.open(version.version_file.name, 'rb') as f:
                file_content = f.read()
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(version.version_file.name)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create response
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{version.version_file.name} (v{version.version_number})"'
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FilePermissionGrantView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, file_id):
        try:
            file_obj = get_object_or_404(File, id=file_id)
            user_id = request.data.get('user_id')
            permission_type = request.data.get('permission_type', 'read')
            expires_at = request.data.get('expires_at')
            
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if permission already exists
            permission, created = FilePermission.objects.get_or_create(
                file=file_obj,
                user=user,
                defaults={
                    'permission_type': permission_type,
                    'granted_by': request.user,
                    'expires_at': expires_at
                }
            )
            
            if not created:
                # Update existing permission
                permission.permission_type = permission_type
                permission.expires_at = expires_at
                permission.save()
            
            serializer = FilePermissionSerializer(permission)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileByTagView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        tag_ids = request.query_params.getlist('tags')
        if not tag_ids:
            return Response({'error': 'At least one tag is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        files = File.objects.filter(tags__id__in=tag_ids).distinct()
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)


class TestAuthView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'message': 'Authentication successful',
            'user': request.user.username,
            'user_id': request.user.id
        })

class TestFileOperationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Test endpoint to check file and folder operations"""
        try:
            # Test folder operations
            folders_count = Folder.objects.count()
            files_count = File.objects.count()
            
            return Response({
                'message': 'File operations test successful',
                'folders_count': folders_count,
                'files_count': files_count,
                'user': request.user.username
            })
        except Exception as e:
            return Response({
                'error': f'File operations test failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileDuplicateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, pk):
        """Duplicate a file"""
        try:
            original_file = get_object_or_404(File, pk=pk)
            
            # Create a copy of the file with proper extension handling
            base_name, extension = os.path.splitext(original_file.name)
            duplicate_name = f"{base_name} (Copy){extension}"
            
            # Ensure the duplicate name is unique
            counter = 1
            while File.objects.filter(name=duplicate_name, folder=original_file.folder).exists():
                counter += 1
                duplicate_name = f"{base_name} (Copy {counter}){extension}"
            
            new_file = File.objects.create(
                name=duplicate_name,
                file=original_file.file,
                file_type=original_file.file_type,
                file_size=original_file.file_size,
                uploaded_by=request.user,
                folder=original_file.folder,
                description=original_file.description
            )
            
            # Copy tags separately (many-to-many relationship)
            if original_file.tags.exists():
                new_file.tags.set(original_file.tags.all())
            
            serializer = FileSerializer(new_file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FolderDuplicateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, pk):
        """Duplicate a folder"""
        try:
            print(f"Starting folder duplication for pk={pk}")
            original_folder = get_object_or_404(Folder, pk=pk)
            print(f"Found original folder: {original_folder.name}")
            
            # Create a copy of the folder with unique naming
            duplicate_name = f"{original_folder.name} (Copy)"
            
            # Ensure the duplicate name is unique
            counter = 1
            while Folder.objects.filter(name=duplicate_name, parent=original_folder.parent).exists():
                counter += 1
                duplicate_name = f"{original_folder.name} (Copy {counter})"
            
            new_folder = Folder.objects.create(
                name=duplicate_name,
                description=original_folder.description,
                created_by=request.user,
                parent=original_folder.parent
            )
            print(f"Created new folder: {new_folder.name}")
            
            # Copy files from original folder to new folder
            files_in_original = File.objects.filter(folder=original_folder)
            print(f"Found {files_in_original.count()} files to copy")
            
            for file_obj in files_in_original:
                print(f"Copying file: {file_obj.name}")
                new_file = File.objects.create(
                    name=file_obj.name,
                    file=file_obj.file,
                    file_type=file_obj.file_type,
                    file_size=file_obj.file_size,
                    uploaded_by=request.user,
                    folder=new_folder,
                    description=file_obj.description
                )
                
                # Copy tags separately (many-to-many relationship)
                if file_obj.tags.exists():
                    print(f"Copying tags for file: {file_obj.name}")
                    new_file.tags.set(file_obj.tags.all())
            
            serializer = FolderSerializer(new_folder)
            print(f"Folder duplication completed successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error duplicating folder: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FolderDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, pk):
        """Download a folder as a ZIP file containing all its contents"""
        try:
            folder = get_object_or_404(Folder, pk=pk)
            print(f"Starting download for folder: {folder.name} (ID: {folder.id})")
            
            # Create a temporary ZIP file
            temp_zip_path = tempfile.mktemp(suffix='.zip')
            
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add all files in the current folder to the ZIP
                files_in_folder = File.objects.filter(folder=folder)
                print(f"Found {files_in_folder.count()} files in folder {folder.name}")
                
                for file_obj in files_in_folder:
                    print(f"Processing file: {file_obj.name}")
                    if file_obj.file:
                        if default_storage.exists(file_obj.file.name):
                            try:
                                # Read file content
                                with default_storage.open(file_obj.file.name, 'rb') as f:
                                    file_content = f.read()
                                
                                # Add to ZIP with the file name
                                zip_file.writestr(file_obj.name, file_content)
                                print(f"Added file to ZIP: {file_obj.name}")
                            except Exception as e:
                                print(f"Error adding file {file_obj.name} to ZIP: {e}")
                                continue
                        else:
                            print(f"File not found in storage: {file_obj.name} (path: {file_obj.file.name})")
                            # Create a placeholder file in the ZIP to indicate the missing file
                            placeholder_content = f"File '{file_obj.name}' was not found in storage.\nThis file may have been deleted or the upload failed.\nOriginal path: {file_obj.file.name}\nFile size in database: {file_obj.get_file_size_display()}"
                            zip_file.writestr(f"MISSING_{file_obj.name}.txt", placeholder_content)
                    else:
                        print(f"File object has no file field: {file_obj.name}")
                
                # Recursively add files from subfolders
                self._add_subfolder_contents(zip_file, folder, folder.name)
            
            # Read the ZIP file content
            with open(temp_zip_path, 'rb') as zip_file:
                zip_content = zip_file.read()
            
            # Clean up the temporary file
            os.unlink(temp_zip_path)
            
            print(f"ZIP file created successfully. Size: {len(zip_content)} bytes")
            
            # Create response with proper headers
            response = HttpResponse(zip_content, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{folder.name}.zip"'
            response['Content-Length'] = len(zip_content)
            
            return response
                
        except Exception as e:
            print(f"Error downloading folder: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _add_subfolder_contents(self, zip_file, folder, base_path):
        """Recursively add contents of subfolders to the ZIP"""
        print(f"Checking subfolders for: {folder.name}")
        for subfolder in folder.children.all():
            subfolder_path = f"{base_path}/{subfolder.name}"
            print(f"Processing subfolder: {subfolder.name} at path: {subfolder_path}")
            
            # Add files in this subfolder
            files_in_subfolder = File.objects.filter(folder=subfolder)
            print(f"Found {files_in_subfolder.count()} files in subfolder {subfolder.name}")
            
            for file_obj in files_in_subfolder:
                print(f"Processing subfolder file: {file_obj.name}")
                if file_obj.file and default_storage.exists(file_obj.file.name):
                    try:
                        with default_storage.open(file_obj.file.name, 'rb') as f:
                            file_content = f.read()
                        zip_file.writestr(f"{subfolder_path}/{file_obj.name}", file_content)
                        print(f"Added subfolder file to ZIP: {subfolder_path}/{file_obj.name}")
                    except Exception as e:
                        print(f"Error adding subfolder file {file_obj.name} to ZIP: {e}")
                        continue
                else:
                    print(f"Subfolder file not found: {file_obj.name}")
            
            # Recursively add subfolders
            self._add_subfolder_contents(zip_file, subfolder, subfolder_path)


class PasswordChangeView(APIView):
    """Allow authenticated users to change their password"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Verify old password
            if not user.check_password(old_password):
                return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """Verify security questions for password reset"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            security_answer = serializer.validated_data.get('security_answer', '')
            professor_lastname = serializer.validated_data['professor_last_name']
            
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Verify professor's last name (always required)
            if professor_lastname.lower() != 'williams':
                return Response({'error': 'Professor last name is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user has security questions set up (optional)
            try:
                security_questions = user.security_questions
                if security_questions.security_answer:
                    # If security questions exist, verify them
                    if not security_questions.verify_security_answer(security_answer):
                        return Response({'error': 'Security answer is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            except UserSecurityQuestions.DoesNotExist:
                # If no security questions set up, that's okay - just verify professor's name
                pass
            
            return Response({'message': 'Verification successful'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Reset password after security questions verification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            security_answer = serializer.validated_data.get('security_answer', '')
            professor_lastname = serializer.validated_data['professor_last_name']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Verify professor's last name (always required)
            if professor_lastname.lower() != 'williams':
                return Response({'error': 'Professor last name is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user has security questions set up (optional)
            try:
                security_questions = user.security_questions
                if security_questions.security_answer:
                    # If security questions exist, verify them
                    if not security_questions.verify_security_answer(security_answer):
                        return Response({'error': 'Security answer is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            except UserSecurityQuestions.DoesNotExist:
                # If no security questions set up, that's okay - just verify professor's name
                pass
            
            # Set new password (skip Django's password validation for resets)
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SecurityQuestionsSetupView(APIView):
    """Allow users to set up security questions"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        serializer = SecurityQuestionsSetupSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check if security questions already exist
            if hasattr(user, 'security_questions'):
                return Response({'error': 'Security questions already set up'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create security questions - professor_last_name is required
            security_questions = UserSecurityQuestions.objects.create(
                user=user,
                security_answer=serializer.validated_data['security_answer'],
                professor_last_name=serializer.validated_data['professor_last_name']
            )
            
            response_serializer = UserSecurityQuestionsSerializer(security_questions)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SecurityQuestionsUpdateView(APIView):
    """Allow users to update their security questions"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def put(self, request):
        serializer = SecurityQuestionsSetupSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Get or create security questions - professor_last_name is required
            security_questions, created = UserSecurityQuestions.objects.get_or_create(
                user=user,
                defaults={
                    'security_answer': serializer.validated_data['security_answer'],
                    'professor_last_name': serializer.validated_data['professor_last_name']
                }
            )
            
            if not created:
                # Update existing security questions
                security_questions.security_answer = serializer.validated_data['security_answer']
                security_questions.professor_last_name = serializer.validated_data['professor_last_name']
                security_questions.save()
            
            response_serializer = UserSecurityQuestionsSerializer(security_questions)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailPasswordResetRequestView(APIView):
    """Send password reset code to user's email"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmailPasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Don't reveal if email exists or not for security
                return Response({'message': 'If an account with this email exists, a reset code has been sent.'}, status=status.HTTP_200_OK)
            
            # Create reset code
            reset_code = PasswordResetCode.create_for_user(user)
            
            # Send email with reset code
            try:
                subject = 'Password Reset Code - Marc-D'
                message = f"""
Hello {user.username},

You have requested a password reset for your Marc-D account.

Your password reset code is: {reset_code.code}

This code will expire in 15 minutes.

If you did not request this password reset, please ignore this email.

Best regards,
The Marc-D Team
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return Response({'message': 'Password reset code sent to your email.'}, status=status.HTTP_200_OK)
                
            except Exception as e:
                # Log the error but don't expose it to the user
                print(f"Error sending email: {e}")
                return Response({'error': 'Failed to send reset code. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailPasswordResetVerifyView(APIView):
    """Verify the reset code"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmailPasswordResetVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Find the reset code
            try:
                reset_code = PasswordResetCode.objects.get(
                    user=user,
                    code=code,
                    is_used=False
                )
            except PasswordResetCode.DoesNotExist:
                return Response({'error': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if code is valid
            if not reset_code.is_valid():
                return Response({'error': 'Reset code has expired or is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Reset code verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailPasswordResetConfirmView(APIView):
    """Reset password using email code"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmailPasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Find the reset code
            try:
                reset_code = PasswordResetCode.objects.get(
                    user=user,
                    code=code,
                    is_used=False
                )
            except PasswordResetCode.DoesNotExist:
                return Response({'error': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if code is valid
            if not reset_code.is_valid():
                return Response({'error': 'Reset code has expired or is invalid.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark code as used
            reset_code.is_used = True
            reset_code.save()
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    """Custom admin login view with logging"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle admin login with logging"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            AdminLoginLog.log_failed_login(
                username or 'unknown',
                request,
                'Missing username or password'
            )
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            # Log failed login
            AdminLoginLog.log_failed_login(
                username,
                request,
                'Invalid credentials'
            )
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_staff:
            # Log failed login for non-staff user
            AdminLoginLog.log_failed_login(
                username,
                request,
                'User is not staff/admin'
            )
            return Response({'error': 'Access denied. Admin privileges required.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Log successful login
        AdminLoginLog.log_successful_login(user, request)
        
        # Perform Django login
        django_login(request, user)
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
        }, status=status.HTTP_200_OK)
    
    def get(self, request):
        """Show admin login form"""
        return render(request, 'admin/login.html')


class AdminLoginLogView(APIView):
    """View admin login logs (admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """Get admin login logs"""
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get query parameters for filtering
        days = request.query_params.get('days', 30)
        user_id = request.query_params.get('user_id')
        success_only = request.query_params.get('success_only', 'false').lower() == 'true'
        
        from django.utils import timezone
        from datetime import timedelta
        
        # Filter by date range
        cutoff_date = timezone.now() - timedelta(days=int(days))
        logs = AdminLoginLog.objects.filter(login_time__gte=cutoff_date)
        
        # Filter by user if specified
        if user_id:
            logs = logs.filter(user_id=user_id)
        
        # Filter by success if specified
        if success_only:
            logs = logs.filter(success=True)
        
        # Prepare response data
        log_data = []
        for log in logs[:100]:  # Limit to 100 most recent
            log_data.append({
                'id': log.id,
                'user': {
                    'id': log.user.id if log.user else None,
                    'username': log.user.username if log.user else 'Unknown'
                },
                'login_time': log.login_time,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'success': log.success,
                'failure_reason': log.failure_reason
            })
        
        return Response({
            'logs': log_data,
            'total_count': logs.count(),
            'successful_logins': logs.filter(success=True).count(),
            'failed_logins': logs.filter(success=False).count()
        }, status=status.HTTP_200_OK)


# Debug endpoint for mobile testing (can be removed in production)
@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def mobile_debug_view(request):
    """Debug endpoint to test mobile requests"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    debug_info = {
        'method': request.method,
        'path': request.path,
        'user_agent': user_agent,
        'is_mobile': any(indicator in user_agent.lower() for indicator in ['mobile', 'android', 'iphone', 'ipad']),
        'csrf_exempt': getattr(request, '_dont_enforce_csrf_checks', False),
        'status': 'Mobile compatibility fixes working correctly!'
    }
    
    return Response(debug_info, status=status.HTTP_200_OK)


# Mobile error reporting endpoint
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def mobile_error_report(request):
    """Endpoint for mobile devices to report errors"""
    try:
        data = request.data
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip = request.META.get('REMOTE_ADDR', '')
        
        error_report = {
            'timestamp': timezone.now().isoformat(),
            'user_agent': user_agent,
            'ip': ip,
            'error_type': data.get('error_type', 'unknown'),
            'error_message': data.get('error_message', ''),
            'error_stack': data.get('error_stack', ''),
            'page_url': data.get('page_url', ''),
            'browser_info': data.get('browser_info', {}),
            'network_info': data.get('network_info', {}),
        }
        
        print(f"MOBILE_ERROR_REPORT: {error_report}")
        
        return Response({
            'status': 'Error reported successfully',
            'error_id': f"ERR-{int(timezone.now().timestamp())}"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error in mobile_error_report: {str(e)}")
        return Response({
            'status': 'Error report received'
        }, status=status.HTTP_200_OK)



