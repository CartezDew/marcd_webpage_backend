# Waitlist Setup Instructions

## Backend Setup (Django)

The waitlist functionality has been successfully set up in your Django backend with the following components:

### 1. Database Model
- **Model**: `WaitlistEntry` in `main_app/models.py`
- **Fields**: 
  - `email` (unique email address)
  - `created_at` (automatic timestamp)

### 2. Email Validation Rules
The system enforces strict email validation on both frontend and backend:

#### ✅ Valid Email Examples
- `user@example.com`
- `user.name@domain.org`
- `test123@company.co.uk`

#### ❌ Invalid Email Examples
- `testexample.com` (missing @ symbol)
- `test@example` (missing domain extension)
- `noemail` (contains 'noemail')
- `test@noemail.com` (contains 'noemail')
- `@example.com` (no username)
- `test@.com` (no domain)
- `test@example.` (no extension)

#### Validation Checks
1. **@ Symbol**: Email must contain @ symbol
2. **Domain Extension**: Email must contain a domain (e.g., .com, .org)
3. **No 'noemail'**: Email cannot be 'noemail' or contain 'noemail'
4. **Format Validation**: Must follow standard email format

### 3. API Endpoints

#### Public Endpoints (No Authentication Required)
- **URL**: `POST /waitlist/` - Submit email to waitlist
- **View**: `WaitlistView` in `main_app/views.py`
- **Serializer**: `WaitlistEntrySerializer` in `main_app/serializers.py`

#### Protected Endpoints (Admin Authentication Required)
- **URL**: `GET /waitlist/list/` - List all waitlist entries
- **URL**: `GET /waitlist-entries/` - List all waitlist entries (ViewSet)
- **URL**: `GET /waitlist-entries/<id>/` - Get specific waitlist entry
- **URL**: `PUT /waitlist-entries/<id>/` - Update waitlist entry
- **URL**: `DELETE /waitlist-entries/<id>/` - Delete waitlist entry
- **Authentication**: Token Authentication required
- **Permissions**: Admin users only

### 4. Admin Interface
- Waitlist entries are available in Django admin at `/admin/`
- You can view, search, and manage all waitlist submissions

## Frontend Integration

### Option 1: Using the provided utility functions

1. Import the utility functions in your React component:
```javascript
import { handleWaitlistSubmission } from './waitlist-api.js';
```

2. Replace your TODO comment with the actual API call:
```javascript
const handleWaitlistSubmit = async (e) => {
  e.preventDefault();
  
  if (!email || emailError) return;
  
  try {
    await handleWaitlistSubmission(
      email,
      (successMessage) => {
        console.log('Success:', successMessage);
        setIsSubmitted(true);
        setEmail('');
        setEmailError('');
        
        // Reset success message after 3 seconds
        setTimeout(() => {
          setIsSubmitted(false);
        }, 3000);
      },
      (errorMessage) => {
        console.error('Error:', errorMessage);
        setEmailError(errorMessage);
      }
    );
  } catch (error) {
    console.error('Submission failed:', error);
    setEmailError('Failed to submit. Please try again.');
  }
};
```

### Option 2: Direct API call

Replace your TODO comment with:
```javascript
const handleWaitlistSubmit = async (e) => {
  e.preventDefault();
  
  if (!email || emailError) return;
  
  try {
    const response = await fetch('http://localhost:8000/waitlist/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();

    if (response.ok) {
      console.log('Successfully added to waitlist:', data);
      setIsSubmitted(true);
      setEmail('');
      setEmailError('');
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        setIsSubmitted(false);
      }, 3000);
    } else {
      setEmailError(data.email?.[0] || data.error || 'Failed to submit to waitlist');
    }
  } catch (error) {
    console.error('Error submitting to waitlist:', error);
    setEmailError('Failed to submit. Please try again.');
  }
};
```

## Testing

### Test the public submission endpoint with valid email:
```bash
curl -X POST http://localhost:8000/waitlist/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Test validation with invalid emails:
```bash
# Missing @ symbol
curl -X POST http://localhost:8000/waitlist/ \
  -H "Content-Type: application/json" \
  -d '{"email": "testexample.com"}'

# Missing domain extension
curl -X POST http://localhost:8000/waitlist/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example"}'

# Contains 'noemail'
curl -X POST http://localhost:8000/waitlist/ \
  -H "Content-Type: application/json" \
  -d '{"email": "noemail"}'
```

### Test the protected list endpoint (requires admin token):
```bash
# First, get an admin token (you'll need to create a superuser first)
curl -X GET http://localhost:8000/waitlist/list/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN"
```

### Expected response for valid submission:
```json
{
  "message": "Successfully added to waitlist!",
  "email": "test@example.com"
}
```

### Expected response for invalid email:
```json
{
  "email": ["Enter a valid email address."]
}
```

### Expected response for list (admin only):
```json
[
  {
    "id": 1,
    "email": "test@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

## Admin Access

### Creating an Admin User
```bash
python manage.py createsuperuser
```

### Getting an Admin Token
1. Create a superuser if you haven't already
2. Access Django admin at `/admin/`
3. Go to "Tokens" section
4. Create a token for your admin user

### Using Admin Endpoints
All protected endpoints require:
- **Header**: `Authorization: Token YOUR_ADMIN_TOKEN`
- **User**: Must be a staff/superuser

## Production Deployment

1. **Update API URL**: Change the `API_BASE_URL` in `waitlist-api.js` to your production domain
2. **CORS Settings**: Ensure your production domain is in `CORS_ALLOWED_ORIGINS` in `settings.py`
3. **Database**: Make sure your production database is properly configured
4. **Admin Tokens**: Create admin tokens for production access

## Database Management

### View waitlist entries:
- Access Django admin at `yourdomain.com/admin/`
- Navigate to "Waitlist Entries" section

### Export waitlist data:
```bash
python manage.py shell
```
```python
from main_app.models import WaitlistEntry
import csv

# Export to CSV
with open('waitlist_export.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Email', 'Date Added'])
    for entry in WaitlistEntry.objects.all():
        writer.writerow([entry.email, entry.created_at])
```

## Security Notes

- **Public endpoint**: Only the submission endpoint (`POST /waitlist/`) is public
- **Protected endpoints**: All list, view, update, and delete operations require admin authentication
- **Email validation**: Comprehensive validation on both frontend and backend
- **Duplicate prevention**: Unique constraint prevents duplicate emails
- **Token authentication**: Admin access requires valid tokens
- **Rate limiting**: Consider adding rate limiting for production use
- **Input sanitization**: All email inputs are validated and sanitized 