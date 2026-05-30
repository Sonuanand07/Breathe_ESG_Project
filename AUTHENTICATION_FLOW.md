# Breathe ESG - Authentication Flow Diagram

## BEFORE (Broken) ❌

```
┌─────────────────┐
│ React Frontend  │
└────────┬────────┘
         │
         │ 1. User enters credentials
         │    analyst@breatheesg.com
         │    demo1234
         │
         v
    ┌─────────────────────────────┐
    │ Generate Fake Token         │
    │ demo-token-YW5hbHlzdEB...  │
    └──────────┬──────────────────┘
               │
               │ 2. Send fake token
               │    Authorization: Token demo-token-YW5hbHlzdEB...
               │
               v
    ┌──────────────────────────────┐
    │ Django Backend               │
    │ /api/clients/                │
    └──────────┬───────────────────┘
               │
               │ 3. Validate token
               │    SELECT * FROM authtoken_token WHERE key = 'demo-token-...'
               │    Result: NOT FOUND
               │
               v
         ❌ 403 Unauthorized
    "Authentication credentials were not provided"
```

---

## AFTER (Fixed) ✅

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOGIN FLOW (NEW)                                │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: User Submits Credentials
┌──────────────────────┐
│ React Login Form     │
├──────────────────────┤
│ Email:    [____]     │
│ Password: [____]     │
│ [Sign In]            │
└─────────┬────────────┘
          │
          │ POST /api/auth/login/
          │ {
          │   "email": "analyst@breatheesg.com",
          │   "password": "demo1234"
          │ }
          │
          v
┌─────────────────────────────────────────┐
│ Django Auth Endpoint                    │
│ apps/core/auth_views.py::login()        │
├─────────────────────────────────────────┤
│ 1. Get email and password               │
│ 2. Validate credentials                 │
│ 3. Get or create User                   │
│ 4. Get or create Token for User         │
│ 5. Return token to frontend             │
└──────────────┬──────────────────────────┘
               │
               │ Response 200 OK
               │ {
               │   "token": "abc123def456xyz...",
               │   "user": {
               │     "id": 1,
               │     "email": "analyst@breatheesg.com",
               │     "name": "Demo Analyst"
               │   }
               │ }
               │
               v
┌──────────────────────────────┐
│ React Frontend               │
├──────────────────────────────┤
│ 1. Receive token             │
│ 2. Store in localStorage     │
│ 3. Update Zustand store      │
│ 4. Redirect to Dashboard     │
└──────────────┬───────────────┘
               │
               │ localStorage.setItem('authToken', 'abc123...')
               │
               v
       ✅ Logged In Successfully

─────────────────────────────────────────────────────────────────────────

Step 2: Authenticated API Calls (ALL SUBSEQUENT CALLS)

┌──────────────────────────────────┐
│ React Component needs data       │
│ useEffect(() => {                │
│   api.getClients()               │
│ }, [])                           │
└─────────┬────────────────────────┘
          │
          │ GET /api/clients/
          │ Headers: {
          │   "Authorization": "Token abc123def456xyz..."
          │ }
          │
          v
┌──────────────────────────────────────────┐
│ Django REST Framework                    │
│ Authentication Middleware                │
├──────────────────────────────────────────┤
│ 1. Extract token from header             │
│ 2. Query database:                       │
│    SELECT * FROM authtoken_token         │
│    WHERE key = 'abc123def456xyz...'      │
│ 3. Token found! Attach User to request   │
└──────────────┬───────────────────────────┘
               │
               │ ✅ Token Valid
               │
               v
┌──────────────────────────────────────────┐
│ ViewSet executes with request.user set   │
│ ClientViewSet.list(request)              │
├──────────────────────────────────────────┤
│ queryset = Client.objects.all()          │
│ return paginated response                │
└──────────────┬───────────────────────────┘
               │
               │ Response 200 OK
               │ [
               │   {"id": "...", "name": "Tech Corp Inc"},
               │   {"id": "...", "name": "Green Manufacturing Ltd"},
               │   ...
               │ ]
               │
               v
        ✅ Data Retrieved Successfully
```

---

## Key Components Involved

### 1. Frontend (React)
```
Login.jsx
  ├─ User enters: email, password
  ├─ POST to /api/auth/login/
  └─ Store returned token
  
api.js
  ├─ Intercept all requests
  ├─ Add "Authorization: Token ..." header
  └─ Send token with every request

store/index.js (Zustand)
  ├─ Store authToken
  ├─ Store user info
  └─ Provide to all components
```

### 2. Backend (Django)
```
auth_views.py (NEW)
  ├─ login() - Generate token
  └─ logout() - Invalidate token

config/settings.py
  ├─ TokenAuthentication enabled
  ├─ INSTALLED_APPS includes authtoken
  └─ CORS configured

config/urls.py
  ├─ /api/auth/login/ → login view
  └─ /api/auth/logout/ → logout view

apps/core/views.py
  ├─ All ViewSets inherit TokenAuthentication
  └─ All require IsAuthenticated permission
```

### 3. Database
```
Django ORM Models:
  ├─ auth_user (Django User model)
  │  ├─ username
  │  ├─ email
  │  └─ password (hashed)
  │
  └─ authtoken_token (Django Token)
     ├─ key (the actual token string)
     └─ user_id (FK to auth_user)

Sample Data:
  ├─ User: analyst@breatheesg.com
  ├─ Password: demo1234 (hashed)
  └─ Token: auto-generated on first login
```

---

## Security Notes

### ✅ What We Do Right
- Tokens are generated by Django, not frontend
- Tokens stored securely in database
- Password hashing (Django built-in)
- HTTPS enforced in production
- CSRF protection included

### ⚠️ For Production (Not in Demo)
- Use HTTPS everywhere
- Set `SECURE_SSL_REDIRECT = True`
- Use secure cookie flags
- Implement token expiration
- Add rate limiting on auth endpoints
- Implement 2FA for sensitive operations
- Use environment-specific settings

---

## Testing the Flow

### Test Authentication
```bash
# Step 1: Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@breatheesg.com","password":"demo1234"}'

# Output:
{
  "token": "abc123def456xyz...",
  "user": {
    "id": 1,
    "email": "analyst@breatheesg.com",
    "name": "Demo Analyst"
  }
}

# Step 2: Use token in subsequent requests
TOKEN="abc123def456xyz..."

curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Token $TOKEN"

# Output: List of clients (200 OK) ✅
```

### Check Token in Database
```bash
# Local SQLite
sqlite3 backend/db.sqlite3 "SELECT id, user_id, key FROM authtoken_token LIMIT 1;"

# Output:
# 1|1|abc123def456xyz...
```

---

## Troubleshooting

### Issue: Still getting 403 after login

**Check 1: Token in localStorage**
```javascript
// In browser console
localStorage.getItem('authToken')
// Should show: Token abc123...
```

**Check 2: Token valid in database**
```bash
# In terminal
sqlite3 backend/db.sqlite3 \
  "SELECT * FROM authtoken_token WHERE key='abc123...'"
# Should return a row
```

**Check 3: Request headers**
DevTools > Network > XHR request > Request Headers:
```
Authorization: Token abc123...
```
If missing, check Axios interceptor in api.js

### Issue: Token generation error

**Check:**
- User was created with `get_or_create`
- No password hashing issue
- `rest_framework.authtoken` in INSTALLED_APPS
- Migrations were run: `python manage.py migrate`

### Issue: Login endpoint not found (404)

**Check:**
- `backend/config/urls.py` has auth routes
- Restart Django server
- Check URL: `/api/auth/login/` (with /api prefix)

---

## Summary

The new authentication system:
1. ✅ Validates credentials against database
2. ✅ Returns real Django tokens
3. ✅ Frontend stores and sends token
4. ✅ Backend validates token on every request
5. ✅ Enables all API operations
6. ✅ Maintains audit trail (can track which user did what)
