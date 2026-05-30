# Breathe ESG - Complete Deployment & Troubleshooting Guide

## Quick Fix Summary

This document covers the fixes applied to resolve the 403 errors and file upload issues.

---

## Issues Fixed

### 1. **Authentication Error (403 - "Authentication credentials were not provided")**

**Problem:** 
- Frontend was sending a fake token (`demo-token-...`)
- Backend required Django Token Authentication 
- No proper login endpoint existed

**Solution:**
- ✅ Created `/api/auth/login/` endpoint in `backend/apps/core/auth_views.py`
- ✅ Updated `LoginComponent` to call the real auth endpoint
- ✅ Added `TokenAuthentication` to Django REST Framework settings
- ✅ Added `rest_framework.authtoken` to `INSTALLED_APPS`

**How it works now:**
1. User enters credentials (analyst@breatheesg.com / demo1234)
2. Frontend POSTs to `/api/auth/login/` 
3. Backend creates/retrieves user and returns Django Token
4. Frontend stores token in localStorage
5. All subsequent requests use this token in headers: `Authorization: Token <token_key>`

---

### 2. **Form Field Accessibility Issues**

**Problem:**
- Form inputs missing `id` and `name` attributes
- Labels not properly associated with form fields
- Browser autofill not working

**Solution:**
- ✅ Added `id` and `name` attributes to all form inputs in `DataIngestion.jsx`
- ✅ Updated `<label>` elements to use `htmlFor` attribute
- ✅ Properly linked radio buttons and selects to their labels

**Fixed fields:**
- `#source-sap`, `#source-utility`, `#source-travel` (radio buttons)
- `#dataSourceInstance` (dropdown select)
- `#csvFile` (file input)

---

### 3. **Data Ingestion Endpoints Not Routing Correctly**

**Problem:**
- Endpoints like `/ingestion/ingest-sap/` weren't being registered
- Using old manual routing approach instead of router registration

**Solution:**
- ✅ Registered `DataIngestionViewSet` in the router in `apps/core/urls.py`
- ✅ Updated URLs to use underscores instead of hyphens: `ingest_sap`, `ingest_utility`, `ingest_travel`
- ✅ Updated frontend API calls to use new endpoint paths

**New endpoint structure:**
```
POST /api/ingestion/ingest_sap/
POST /api/ingestion/ingest_utility/
POST /api/ingestion/ingest_travel/
```

---

## Setup Instructions

### Local Development Setup

#### Step 1: Backend Setup
```powershell
cd backend

# Create virtual environment
python -m venv venv
& "venv\Scripts\Activate.ps1"

# Install dependencies
pip install -r requirements.txt

# Create .env from example
copy .env.example .env

# Run migrations
python manage.py migrate

# Populate sample data
python manage.py populate_sample_data

# Or use the initialize script
python initialize.py

# Start server
python manage.py runserver
```

#### Step 2: Frontend Setup
```powershell
cd frontend

# Install dependencies
npm install

# Create .env file
# Add: REACT_APP_API_URL=http://localhost:8000/api

# Start dev server
npm start
```

#### Step 3: Login
- **URL:** http://localhost:3000
- **Email:** analyst@breatheesg.com
- **Password:** demo1234

---

### Deployment on Render/Vercel

#### Backend (Render)

**Environment Variables:**
```
DEBUG=False
SECRET_KEY=<generate_random_key>
ALLOWED_HOSTS=your-app.onrender.com,localhost
DB_ENGINE=django.db.backends.postgresql
DB_NAME=breathe_esg
DB_USER=postgres
DB_PASSWORD=<your_password>
DB_HOST=<your_postgres_host>
DB_PORT=5432
FRONTEND_URL=https://your-frontend.vercel.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py populate_sample_data
```

**Start Command:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

#### Frontend (Vercel)

**Environment Variables:**
```
REACT_APP_API_URL=https://your-backend.onrender.com/api
```

**Build Command:**
```bash
npm install && npm run build
```

---

## Testing the Fixes

### 1. Test Authentication
```bash
# Terminal 1: Start backend
cd backend
python manage.py runserver

# Terminal 2: Test login endpoint
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@breatheesg.com","password":"demo1234"}'

# Expected response:
# {"token":"<token_key>","user":{"id":1,"email":"analyst@breatheesg.com","name":"Demo Analyst"}}
```

### 2. Test Client Loading
```bash
# Replace TOKEN with actual token from login
curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Token <TOKEN>"

# Expected response: List of clients in JSON format
```

### 3. Test Data Source Loading
```bash
curl -X GET "http://localhost:8000/api/data-sources/?client=<client_id>" \
  -H "Authorization: Token <TOKEN>"

# Expected response: List of data sources for the client
```

### 4. Test File Upload
Use the web UI:
1. Login with demo credentials
2. Select a client from sidebar
3. Select data source type (SAP, Utility, or Travel)
4. Select data source instance
5. Choose a CSV file
6. Click "Upload & Ingest Data"

---

## Common Issues & Solutions

### Issue: "Please select a client from the sidebar first"

**Cause:** Client list not loading due to authentication failure

**Solution:**
1. Check browser console for error messages
2. Verify token is being sent: `localStorage.getItem('authToken')`
3. Check backend logs for permission errors
4. Ensure `/api/auth/login/` endpoint is working

### Issue: "Failed to load data sources"

**Cause:** Client filtering not working or client ID invalid

**Solution:**
1. Select a client from sidebar first
2. Check that client ID is correctly passed to the API
3. Verify in browser DevTools > Network tab that the request includes `?client=<id>`

### Issue: File upload fails silently

**Cause:** FormData not being sent correctly or CORS blocking

**Solution:**
1. Check backend logs for the actual error
2. Verify Content-Type header is `multipart/form-data`
3. Ensure CORS_ALLOWED_ORIGINS includes your frontend URL
4. Check that all required fields (file, client_id, data_source_id) are present

### Issue: 403 errors on deployed version

**Cause:** CORS not configured or token not being sent

**Solution:**
1. Update `CORS_ALLOWED_ORIGINS` in backend environment variables
2. Verify `FRONTEND_URL` matches your frontend deployment URL
3. Ensure frontend is sending token: check Network tab in DevTools
4. Check browser console for CORS errors

---

## Database

### SQLite (Local Development)
- File location: `backend/db.sqlite3`
- No setup required, created automatically on first run
- Perfect for testing and development

### PostgreSQL (Production)
- Set `DB_ENGINE=django.db.backends.postgresql`
- Required environment variables: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Run migrations after deployment: `python manage.py migrate`

---

## Verification Checklist

After deployment, verify the following:

- [ ] `/api/auth/login/` returns a token
- [ ] Token is stored in localStorage after login
- [ ] Clients list loads without 403 errors
- [ ] Can select a client and see data sources
- [ ] File upload form has proper id/name attributes (check DevTools)
- [ ] Can upload and ingest sample CSV files
- [ ] Sample data appears in Records list
- [ ] Can approve/reject/flag records
- [ ] All CORS headers are correct in API responses

---

## Files Modified

1. **Backend**
   - `backend/config/settings.py` - Added TokenAuthentication
   - `backend/config/urls.py` - Added auth endpoints
   - `backend/apps/core/urls.py` - Fixed routing
   - `backend/apps/core/auth_views.py` - Created (NEW)
   - `backend/apps/core/management/commands/populate_sample_data.py` - Created (NEW)
   - `backend/initialize.py` - Created (NEW)

2. **Frontend**
   - `frontend/src/components/Login.jsx` - Real auth endpoint
   - `frontend/src/components/DataIngestion.jsx` - Added id/name attributes
   - `frontend/src/services/api.js` - Added login method, fixed endpoints

---

## Need More Help?

Check these files for detailed configuration:
- `DATABASE_SETUP.md` - Database configuration guide
- `DEPLOY.md` - Deployment instructions
- `QUICKSTART.md` - Quick start guide
- `.env.example` - Environment variables template
