from django.contrib import admin
from .models import ContactUs, WaitlistEntry, File, Folder, FileTag, FileVersion, FilePermission, FilePreview

# Register your models here.

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['contact_id', 'first_name', 'last_name', 'email', 'feedback_type', 'created_at', 'is_read']
    list_filter = ['feedback_type', 'created_at', 'is_read']
    search_fields = ['first_name', 'last_name', 'email', 'message']
    readonly_fields = ['contact_id', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_by', 'created_at', 'children_count', 'files_count']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Subfolders'
    
    def files_count(self, obj):
        return obj.files.count()
    files_count.short_description = 'Files'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'folder', 'uploaded_by', 'file_size_display', 'file_type', 'uploaded_at', 'version_count', 'is_public']
    list_filter = ['file_type', 'uploaded_at', 'uploaded_by', 'folder', 'is_public', 'tags']
    search_fields = ['name', 'uploaded_by__username', 'folder__name', 'description']
    readonly_fields = ['uploaded_at', 'file_size', 'file_type', 'version_count']
    filter_horizontal = ['tags']
    ordering = ['name']
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'Size'
    
    def version_count(self, obj):
        return obj.get_version_count()
    version_count.short_description = 'Versions'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(FileTag)
class FileTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_by', 'files_count', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name']
    readonly_fields = ['created_at']
    ordering = ['name']
    
    def files_count(self, obj):
        return obj.files.count()
    files_count.short_description = 'Files'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    list_display = ['file', 'version_number', 'file_size_display', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['file__name', 'change_description']
    readonly_fields = ['created_at', 'file_size']
    ordering = ['-created_at']
    
    def file_size_display(self, obj):
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_display.short_description = 'Size'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(FilePermission)
class FilePermissionAdmin(admin.ModelAdmin):
    list_display = ['file', 'user', 'permission_type', 'granted_by', 'granted_at', 'expires_at', 'is_expired']
    list_filter = ['permission_type', 'granted_at', 'granted_by']
    search_fields = ['file__name', 'user__username', 'granted_by__username']
    readonly_fields = ['granted_at']
    ordering = ['-granted_at']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(FilePreview)
class FilePreviewAdmin(admin.ModelAdmin):
    list_display = ['file', 'generated_at']
    list_filter = ['generated_at']
    search_fields = ['file__name']
    readonly_fields = ['generated_at']
    ordering = ['-generated_at']
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
