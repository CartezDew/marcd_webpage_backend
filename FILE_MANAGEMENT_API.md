# Enhanced File Management API Documentation

This document describes the comprehensive backend routes for file and folder management in the admin dashboard, including advanced features like versioning, permissions, tags, and search.

## Authentication

All endpoints require admin authentication. Use JWT tokens or token authentication.

## Core File Management Endpoints

### 1. List Files
**GET** `/api/files/`

Returns a list of all files. Supports filtering by folder and tags.

**Query Parameters:**
- `folder` (optional): Filter files by folder ID. Use `null` for root level files.
- `search` (optional): Search files by name, file type, or uploader username.
- `tags` (optional): Filter by tag IDs (comma-separated).

**Response:**
```json
[
  {
    "id": 1,
    "name": "document.pdf",
    "folder": 1,
    "full_path": "Documents/document.pdf",
    "file_size": 1024000,
    "file_size_display": "1000.0 KB",
    "file_type": ".pdf",
    "uploaded_by": 1,
    "uploaded_by_username": "admin",
    "uploaded_at": "2024-01-01T12:00:00Z",
    "description": "Important document",
    "tags": [
      {"id": 1, "name": "Important", "color": "#ff0000"}
    ],
    "is_public": false,
    "version_count": 3,
    "latest_version": 3
  }
]
```

### 2. Upload File
**POST** `/api/files/upload/`

Upload a new file to the system.

**Form Data:**
- `file` (required): The file to upload
- `folder` (optional): ID of the folder to upload to
- `name` (optional): Custom name for the file (if not provided, uses original filename)
- `description` (optional): File description
- `tags` (optional): Comma-separated tag IDs
- `is_public` (optional): Boolean to make file public

**Response:**
```json
{
  "id": 1,
  "name": "document.pdf",
  "folder": 1,
  "full_path": "Documents/document.pdf",
  "file_size": 1024000,
  "file_size_display": "1000.0 KB",
  "file_type": ".pdf",
  "uploaded_by": 1,
  "uploaded_by_username": "admin",
  "uploaded_at": "2024-01-01T12:00:00Z",
  "description": "Important document",
  "tags": [],
  "is_public": false,
  "version_count": 1,
  "latest_version": 1
}
```

### 3. Update File
**PATCH** `/api/files/{id}/`

Update file properties including name, description, and other metadata.

**Request Body:**
```json
{
  "name": "new_filename.txt",
  "description": "Updated file description",
  "is_public": true
}
```

**Response:** Updated file object

### 4. Delete File
**DELETE** `/api/files/{id}/`

Delete a file by ID.

**Response:** 204 No Content

### 5. Move File
**POST** `/api/files/{id}/move/`

Move a file to a different folder.

**Request Body:**
```json
{
  "target_folder": 2
}
```

**Response:** Updated file object

### 5. Download File
**GET** `/api/files/{id}/download/`

Download a file by ID. Returns the file as an attachment.

**Response:** File download with appropriate Content-Type and Content-Disposition headers.

## Enhanced File Features

### 6. File Search
**GET** `/api/files/search/`

Full-text search across file names and descriptions using PostgreSQL.

**Query Parameters:**
- `q` (required): Search query

**Response:**
```json
[
  {
    "id": 1,
    "name": "document.pdf",
    "full_path": "Documents/document.pdf",
    "file_size": 1024000,
    "file_size_display": "1000.0 KB",
    "file_type": ".pdf",
    "uploaded_by_username": "admin",
    "uploaded_at": "2024-01-01T12:00:00Z",
    "description": "Important document",
    "tags": [],
    "is_public": false,
    "version_count": 3,
    "latest_version": 3
  }
]
```

### 7. Files by Tags
**GET** `/api/files/by-tags/`

Get files filtered by specific tags.

**Query Parameters:**
- `tags` (required): Tag IDs (can be multiple)

**Response:** Array of file objects

## File Versioning

### 8. List File Versions
**GET** `/api/files/{file_id}/versions/`

Get all versions of a specific file.

**Response:**
```json
[
  {
    "id": 1,
    "file": 1,
    "version_number": 3,
    "version_file": "/media/uploads/versions/document_v3.pdf",
    "file_size": 1024000,
    "file_size_display": "1000.0 KB",
    "created_at": "2024-01-01T12:00:00Z",
    "created_by": 1,
    "created_by_username": "admin",
    "change_description": "Updated content"
  }
]
```

### 9. Upload New Version
**POST** `/api/files/{file_id}/versions/upload/`

Upload a new version of an existing file.

**Form Data:**
- `file` (required): The new version file
- `change_description` (optional): Description of changes

**Response:** New version object

### 10. Download Specific Version
**GET** `/api/files/{file_id}/versions/{version_number}/download/`

Download a specific version of a file.

**Response:** File download with version number in filename

## File Permissions

### 11. List File Permissions
**GET** `/api/files/{file_id}/permissions/`

Get all permissions for a specific file.

**Response:**
```json
[
  {
    "id": 1,
    "file": 1,
    "user": 2,
    "user_username": "john",
    "permission_type": "read",
    "granted_by": 1,
    "granted_by_username": "admin",
    "granted_at": "2024-01-01T12:00:00Z",
    "expires_at": "2024-02-01T12:00:00Z",
    "is_expired": false
  }
]
```

### 12. Grant File Permission
**POST** `/api/files/{file_id}/permissions/grant/`

Grant permission to a user for a specific file.

**Request Body:**
```json
{
  "user_id": 2,
  "permission_type": "read",
  "expires_at": "2024-02-01T12:00:00Z"
}
```

**Response:** Permission object

## File Tags Management

### 13. List Tags
**GET** `/api/tags/`

Get all available tags.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Important",
    "color": "#ff0000",
    "files_count": 5,
    "created_by": 1,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### 14. Create Tag
**POST** `/api/tags/`

Create a new tag.

**Request Body:**
```json
{
  "name": "Important",
  "color": "#ff0000"
}
```

**Response:** Created tag object

### 15. Update Tag
**PUT** `/api/tags/{id}/`

Update an existing tag.

**Request Body:**
```json
{
  "name": "Very Important",
  "color": "#ff0000"
}
```

**Response:** Updated tag object

### 16. Delete Tag
**DELETE** `/api/tags/{id}/`

Delete a tag.

**Response:** 204 No Content

## Folder Management Endpoints

### 17. List Folders
**GET** `/api/folders/`

Returns a list of all folders. Supports filtering by parent folder.

**Query Parameters:**
- `parent` (optional): Filter folders by parent ID. Use `null` for root level folders.
- `search` (optional): Search folders by name or creator username.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Documents",
    "parent": null,
    "full_path": "Documents",
    "children_count": 2,
    "files_count": 5,
    "created_by": 1,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

### 18. Create Folder
**POST** `/api/folders/`

Create a new folder.

**Request Body:**
```json
{
  "name": "New Folder",
  "parent": 1
}
```

**Response:** Created folder object

### 19. Get Folder Details
**GET** `/api/folders/{id}/`

Get detailed information about a specific folder.

**Response:** Folder object

### 20. Update Folder
**PATCH** `/api/folders/{id}/`

Update folder properties including name and description.

**Request Body:**
```json
{
  "name": "Updated Folder Name",
  "description": "Updated folder description"
}
```

**Response:** Updated folder object

### 21. Delete Folder
**DELETE** `/api/folders/{id}/`

Delete a folder and all its contents (files and subfolders).

**Response:** 204 No Content

### 22. Move Folder
**POST** `/api/folders/{id}/move/`

Move a folder to a different parent folder.

**Request Body:**
```json
{
  "target_parent": 3
}
```

**Response:** Updated folder object

## File Previews

### 23. List File Previews
**GET** `/api/previews/`

Get all file previews.

**Response:**
```json
[
  {
    "id": 1,
    "file": 1,
    "thumbnail": "/media/thumbnails/document_thumb.jpg",
    "preview_data": {"text_preview": "First 500 characters..."},
    "generated_at": "2024-01-01T12:00:00Z"
  }
]
```

### 24. Get File Preview
**GET** `/api/previews/{id}/`

Get preview for a specific file.

**Response:** Preview object

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

**400 Bad Request:**
```json
{
  "error": "A file with this name already exists in this folder"
}
```

**401 Unauthorized:**
```json
{
  "error": "Authentication credentials were not provided"
}
```

**404 Not Found:**
```json
{
  "error": "File not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "An unexpected error occurred"
}
```

## File and Folder Naming Rules

- Names cannot contain: `<`, `>`, `:`, `"`, `|`, `?`, `*`, `\`, `/`
- Reserved names are not allowed: `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`
- File and folder names must be unique within the same parent folder

## Permission Types

- `read`: User can view and download the file
- `write`: User can edit and upload new versions
- `admin`: User has full control over the file

## Admin Interface

The enhanced file and folder management is available through the Django admin interface at `/admin/`:

- **Files**: View, create, edit, and delete files with version tracking
- **Folders**: View, create, edit, and delete folders with hierarchical structure
- **File Tags**: Manage tags with colors and file associations
- **File Versions**: Track file version history and changes
- **File Permissions**: Manage user access to files
- **File Previews**: Handle file thumbnails and previews

## File Storage

- Files are stored in the `media/uploads/` directory
- File versions are stored in `media/uploads/versions/`
- Thumbnails are stored in `media/thumbnails/`
- File metadata is stored in the database
- File size and type are automatically detected and stored
- Human-readable file sizes are provided in responses

## Advanced Features

### Full-Text Search
- Uses PostgreSQL's full-text search capabilities
- Searches across file names and descriptions
- Returns ranked results based on relevance

### File Versioning
- Automatic version numbering
- Change descriptions for each version
- Download specific versions
- Track version history

### Permission System
- Granular user permissions
- Time-based expiration
- Multiple permission types
- Audit trail of permission grants

### Tagging System
- Color-coded tags
- Multiple tags per file
- Tag-based filtering
- Tag usage statistics

### Preview System
- Thumbnail generation for images
- Text previews for documents
- JSON-based preview data storage

## Security Features

- Admin-only access to all endpoints
- File type validation
- File size tracking
- Hierarchical folder structure with validation
- Prevention of circular folder references
- Unique naming constraints within folders
- Permission-based access control
- Time-based permission expiration
- Audit trails for all operations 