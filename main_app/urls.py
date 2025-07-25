from django.urls import path
from .views import (
    Landing,
    FeaturesView,
    ContactView,
    ContactUsViewSet,
    WaitlistView,
    WaitlistListView,
    WaitlistEntryViewSet,
    FileViewSet,
    FolderViewSet,
    FileUploadView,
    FileDownloadView,
    FileMoveView,
    FolderMoveView,
    FileTagViewSet,
    FileVersionViewSet,
    FilePermissionViewSet,
    FilePreviewViewSet,
    FileSearchView,
    FileVersionUploadView,
    FileVersionDownloadView,
    FilePermissionGrantView,
    FileByTagView,
    TestAuthView,
)

urlpatterns = [
    path('', Landing.as_view(), name='landing'),
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('waitlist/', WaitlistView.as_view(), name='waitlist'),
    path('waitlist/list/', WaitlistListView.as_view(), name='waitlist-list'),
    path('waitlist-entries/', WaitlistEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='waitlist-entries-list'),
    path('waitlist-entries/<int:id>/', WaitlistEntryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='waitlist-entries-detail'),
    path('contactus/', ContactUsViewSet.as_view({'get': 'list', 'post': 'create'}), name='contactus-list'),
    path('contactus/<str:contact_id>/', ContactUsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='contactus-detail'),
    
    # Test authentication endpoint
    path('api/test-auth/', TestAuthView.as_view(), name='test-auth'),
    
    # File management routes
    path('api/files/', FileViewSet.as_view({'get': 'list'}), name='files-list'),
    path('api/files/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/files/<int:pk>/', FileViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='file-detail'),
    path('api/files/<int:pk>/move/', FileMoveView.as_view(), name='file-move'),
    path('api/files/<int:pk>/download/', FileDownloadView.as_view(), name='file-download'),
    path('api/files/search/', FileSearchView.as_view(), name='file-search'),
    path('api/files/by-tags/', FileByTagView.as_view(), name='files-by-tags'),
    
    # File versioning routes
    path('api/files/<int:file_id>/versions/', FileVersionViewSet.as_view({'get': 'list'}), name='file-versions-list'),
    path('api/files/<int:file_id>/versions/upload/', FileVersionUploadView.as_view(), name='file-version-upload'),
    path('api/files/<int:file_id>/versions/<int:version_number>/download/', FileVersionDownloadView.as_view(), name='file-version-download'),
    
    # File permissions routes
    path('api/files/<int:file_id>/permissions/', FilePermissionViewSet.as_view({'get': 'list'}), name='file-permissions-list'),
    path('api/files/<int:file_id>/permissions/grant/', FilePermissionGrantView.as_view(), name='file-permission-grant'),
    
    # Folder management routes
    path('api/folders/', FolderViewSet.as_view({'get': 'list', 'post': 'create'}), name='folders-list'),
    path('api/folders/<int:pk>/', FolderViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='folders-detail'),
    path('api/folders/<int:pk>/move/', FolderMoveView.as_view(), name='folder-move'),
    
    # File tags routes
    path('api/tags/', FileTagViewSet.as_view({'get': 'list', 'post': 'create'}), name='tags-list'),
    path('api/tags/<int:id>/', FileTagViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='tags-detail'),
    
    # File previews routes
    path('api/previews/', FilePreviewViewSet.as_view({'get': 'list'}), name='previews-list'),
    path('api/previews/<int:id>/', FilePreviewViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='previews-detail'),
]
