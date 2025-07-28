"""
Custom middleware for the main_app
"""
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt


class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """
    Disable CSRF protection for API endpoints that start with /api/ or /login/
    """
    
    def process_request(self, request):
        # List of URL prefixes that should be exempt from CSRF
        csrf_exempt_prefixes = [
            '/api/',
            '/login/',
            '/auth/',
        ]
        
        # Check if the request path starts with any of the exempt prefixes
        if any(request.path.startswith(prefix) for prefix in csrf_exempt_prefixes):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return None 