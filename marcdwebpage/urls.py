"""
URL configuration for marcdwebpage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from main_app.views import CustomTokenObtainPairView, MobileLoginTestView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),  # Alias for frontend compatibility
    path('api/login/', CustomTokenObtainPairView.as_view(), name='api_login'),  # Additional alias
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),  # Additional alias
    path('api/signin/', CustomTokenObtainPairView.as_view(), name='signin'),  # Additional alias
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login_short'),  # Additional alias
    path('api/test-mobile/', MobileLoginTestView.as_view(), name='mobile_test'),  # Debug endpoint
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
