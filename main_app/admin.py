from django.contrib import admin
from .models import Folder, File, FileTag, FileVersion, FilePermission, FilePreview, WaitlistEntry, ContactSubmission, ContactUs, UserSecurityQuestions, PasswordResetCode, AdminLoginLog


class FileInline(admin.TabularInline):
    model = File
    readonly_fields = ['uploaded_at', 'file_size', 'file_type']
    extra = 0


class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_by', 'created_at', 'files_list']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'files_list']
    inlines = [FileInline]
    
    def files_list(self, obj):
        files = obj.files.all()
        if files:
            return ', '.join([f.name for f in files[:5]])
        return 'No files'
    files_list.short_description = 'Files in folder'


class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'folder', 'uploaded_by', 'get_file_size_display', 'file_type', 'uploaded_at', 'file_exists']
    list_filter = ['file_type', 'uploaded_at', 'folder', 'uploaded_by']
    search_fields = ['name', 'description', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'file_exists']
    
    def get_file_size_display(self, obj):
        return obj.get_file_size_display()
    get_file_size_display.short_description = 'Size'
    
    def file_exists(self, obj):
        if obj.file:
            from django.core.files.storage import default_storage
            return default_storage.exists(obj.file.name)
        return False
    file_exists.boolean = True
    file_exists.short_description = 'File Exists'


class FileTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name']


class FileVersionAdmin(admin.ModelAdmin):
    list_display = ['file', 'version_number', 'created_by', 'created_at', 'get_file_size_display']
    list_filter = ['created_at', 'created_by', 'file']
    search_fields = ['file__name', 'change_description']
    
    def get_file_size_display(self, obj):
        return obj.get_file_size_display()
    get_file_size_display.short_description = 'Size'


class FilePermissionAdmin(admin.ModelAdmin):
    list_display = ['file', 'user', 'permission_type', 'granted_by', 'granted_at', 'is_expired']
    list_filter = ['permission_type', 'granted_at', 'granted_by']
    search_fields = ['file__name', 'user__username', 'granted_by__username']


class FilePreviewAdmin(admin.ModelAdmin):
    list_display = ['file', 'generated_at']
    list_filter = ['generated_at']
    search_fields = ['file__name']


class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_id', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['email', 'entry_id']
    readonly_fields = ['entry_id', 'created_at']


class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['contact_id', 'first_name', 'last_name', 'email', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['first_name', 'last_name', 'email', 'contact_id']
    readonly_fields = ['contact_id', 'submitted_at']


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['contact_id', 'first_name', 'last_name', 'email', 'feedback_type', 'created_at', 'is_read']
    list_filter = ['feedback_type', 'created_at', 'is_read']
    search_fields = ['first_name', 'last_name', 'email', 'contact_id']
    readonly_fields = ['contact_id', 'created_at']


class UserSecurityQuestionsAdmin(admin.ModelAdmin):
    list_display = ['user', 'security_answer', 'professor_last_name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at', 'expires_at', 'is_used', 'is_valid']
    list_filter = ['created_at', 'expires_at', 'is_used']
    search_fields = ['user__username', 'user__email', 'code']
    readonly_fields = ['created_at', 'expires_at', 'is_valid']
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'


class AdminLoginLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'ip_address', 'success', 'failure_reason']
    list_filter = ['login_time', 'success', 'ip_address']
    search_fields = ['user__username', 'ip_address', 'failure_reason']
    readonly_fields = ['login_time', 'ip_address', 'user_agent', 'success', 'failure_reason']
    ordering = ['-login_time']
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of log entries
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing of log entries
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can delete logs


admin.site.register(Folder, FolderAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(FileTag, FileTagAdmin)
admin.site.register(FileVersion, FileVersionAdmin)
admin.site.register(FilePermission, FilePermissionAdmin)
admin.site.register(FilePreview, FilePreviewAdmin)
admin.site.register(WaitlistEntry, WaitlistEntryAdmin)
admin.site.register(ContactSubmission, ContactSubmissionAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(UserSecurityQuestions, UserSecurityQuestionsAdmin)
admin.site.register(PasswordResetCode, PasswordResetCodeAdmin)
admin.site.register(AdminLoginLog, AdminLoginLogAdmin)
