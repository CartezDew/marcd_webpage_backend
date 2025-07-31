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
    FolderDownloadView,
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
    FileDuplicateView,
    FolderDuplicateView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    SecurityQuestionsSetupView,
    SecurityQuestionsUpdateView,
    EmailPasswordResetRequestView,
    EmailPasswordResetVerifyView,
    EmailPasswordResetConfirmView,
    AdminLoginView,
    AdminLoginLogView,
    mobile_debug_view,
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
    path('contactus/<int:id>/', ContactUsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='contactus-detail'),
    
    # Test authentication endpoint
    path('api/test-auth/', TestAuthView.as_view(), name='test-auth'),
    path('api/debug/mobile/', mobile_debug_view, name='mobile_debug'),
    
    # Admin login and logging routes
    path('api/admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('api/admin/login-logs/', AdminLoginLogView.as_view(), name='admin-login-logs'),
    
    # Password management routes
    path('api/password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('api/password/reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('api/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('api/password/reset/email/request/', EmailPasswordResetRequestView.as_view(), name='email-password-reset-request'),
    path('api/password/reset/email/verify/', EmailPasswordResetVerifyView.as_view(), name='email-password-reset-verify'),
    path('api/password/reset/email/confirm/', EmailPasswordResetConfirmView.as_view(), name='email-password-reset-confirm'),
    path('api/security-questions/setup/', SecurityQuestionsSetupView.as_view(), name='security-questions-setup'),
    path('api/security-questions/update/', SecurityQuestionsUpdateView.as_view(), name='security-questions-update'),
    
    # File management routes
    path('api/files/', FileViewSet.as_view({'get': 'list'}), name='files-list'),
    path('api/files/upload/', FileUploadView.as_view(), name='file-upload'),
    path('api/files/<int:pk>/', FileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='file-detail'),
    path('api/files/<int:pk>/move/', FileMoveView.as_view(), name='file-move'),
    path('api/files/<int:pk>/download/', FileDownloadView.as_view(), name='file-download'),
    path('api/files/<int:pk>/duplicate/', FileDuplicateView.as_view(), name='file-duplicate'),
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
    path('api/folders/<int:pk>/duplicate/', FolderDuplicateView.as_view(), name='folder-duplicate'),
    path('api/folders/<int:pk>/download/', FolderDownloadView.as_view(), name='folder-download'),
    
    # File tags routes
    path('api/file-tags/', FileTagViewSet.as_view({'get': 'list', 'post': 'create'}), name='file-tags-list'),
    path('api/file-tags/<int:pk>/', FileTagViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='file-tags-detail'),
    
    # File preview routes
    path('api/file-previews/', FilePreviewViewSet.as_view({'get': 'list'}), name='file-previews-list'),
    path('api/file-previews/<int:pk>/', FilePreviewViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='file-previews-detail'),
]
