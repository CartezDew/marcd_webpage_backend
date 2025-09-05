"""
Custom middleware for the main_app
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.conf import settings
import re


class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """
    Disable CSRF protection for API endpoints that start with /api/ or /login/
    Enhanced for mobile compatibility
    """
    
    def process_request(self, request):
        # List of URL prefixes that should be exempt from CSRF
        csrf_exempt_prefixes = [
            '/api/',
            '/login/',
            '/auth/',
            '/waitlist/',
            '/contactus/',
        ]
        
        # Check if the request path starts with any of the exempt prefixes
        if any(request.path.startswith(prefix) for prefix in csrf_exempt_prefixes):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        # Enhanced mobile-specific CSRF exemption
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_indicators = [
            'mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'webos',
            'windows phone', 'opera mini', 'kindle', 'silk', 'fennec', 'mobile safari',
            'mobile chrome', 'mobile firefox', 'mobile edge', 'mobile opera'
        ]
        
        if any(indicator in user_agent for indicator in mobile_indicators):
            # For mobile devices, be more lenient with CSRF for specific endpoints
            mobile_exempt_paths = ['/waitlist/', '/contactus/', '/api/login/', '/login/', '/api/token/', '/api/auth/']
            if any(request.path.startswith(path) for path in mobile_exempt_paths):
                setattr(request, '_dont_enforce_csrf_checks', True)
                # Add mobile-specific flag for debugging
                setattr(request, '_mobile_device', True)
        
        return None 


class MobileCompatibilityMiddleware(MiddlewareMixin):
    """Add mobile-friendly headers and handle mobile-specific issues"""
    
    def process_response(self, request, response):
        # Add mobile-friendly headers
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_indicators = [
            'mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'webos',
            'windows phone', 'opera mini', 'kindle', 'silk', 'fennec', 'mobile safari',
            'mobile chrome', 'mobile firefox', 'mobile edge', 'mobile opera'
        ]
        
        is_mobile = any(indicator in user_agent for indicator in mobile_indicators)
        
        if is_mobile:
            # Add headers for mobile compatibility
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, User-Agent'
            response['Access-Control-Max-Age'] = '86400'
            response['Access-Control-Allow-Credentials'] = 'true'
            
            # Prevent mobile caching issues
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Add mobile-specific headers
            response['X-Mobile-Device'] = 'true'
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'SAMEORIGIN'
        
        return response


class AdminLoginLoggingMiddleware(MiddlewareMixin):
    """Middleware to automatically log admin login attempts"""
    
    def process_request(self, request):
        # Only process admin login requests
        if request.path == '/admin/login/' and request.method == 'POST':
            # Store request info for logging in process_response
            request._admin_login_attempt = True
            request._admin_login_data = {
                'username': request.POST.get('username', ''),
                'password': request.POST.get('password', ''),
            }
        return None
    
    def process_response(self, request, response):
        # Check if this was an admin login attempt
        if hasattr(request, '_admin_login_attempt'):
            username = request._admin_login_data.get('username', '')
            
            # Check if login was successful
            if response.status_code == 302 and 'admin/' in response.get('Location', ''):
                # Successful login - find the user
                from django.contrib.auth import get_user
                try:
                    user = get_user(request)
                    if user and not isinstance(user, AnonymousUser):
                        from .models import AdminLoginLog
                        AdminLoginLog.log_successful_login(user, request)
                except Exception as e:
                    print(f"Error logging successful admin login: {e}")
            else:
                # Failed login
                from .models import AdminLoginLog
                failure_reason = 'Invalid credentials'
                if not username:
                    failure_reason = 'Missing username'
                elif not request._admin_login_data.get('password'):
                    failure_reason = 'Missing password'
                
                AdminLoginLog.log_failed_login(username, request, failure_reason)
        
        return response 