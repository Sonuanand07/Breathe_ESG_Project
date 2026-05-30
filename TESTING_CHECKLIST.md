# Breathe ESG - Testing & Verification Guide

## Pre-Deployment Checklist

### Backend Setup ✓

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example`
- [ ] Database migrations run: `python manage.py migrate`
- [ ] Sample data loaded: `python manage.py populate_sample_data`
- [ ] Server starts: `python manage.py runserver`

### Frontend Setup ✓

- [ ] Node.js 16+ installed
- [ ] Dependencies installed: `npm install`
- [ ] `.env` file created with `REACT_APP_API_URL`
- [ ] Dev server starts: `npm start`

---

## API Testing

### 1. Health Check
```bash
curl http://localhost:8000/
# Expected: {"status":"ok"}
```

### 2. Authentication Flow

#### 2.1 Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@breatheesg.com","password":"demo1234"}'

# Expected response:
# {
#   "token": "abc123def456...",
#   "user": {
#     "id": 1,
#     "email": "analyst@breatheesg.com",
#     "name": "Demo Analyst"
#   }
# }
```

#### 2.2 Store Token
```powershell
# In PowerShell, save the token
$TOKEN = "abc123def456..."
```

#### 2.3 Test Authenticated Request
```bash
curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Token $TOKEN"

# Expected: List of clients
```

### 3. Client Operations

#### 3.1 List Clients
```bash
curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Token $TOKEN"
```

#### 3.2 Get Client Details
```bash
curl -X GET http://localhost:8000/api/clients/{client_id}/ \
  -H "Authorization: Token $TOKEN"
```

### 4. Data Source Operations

#### 4.1 List Data Sources
```bash
curl -X GET "http://localhost:8000/api/data-sources/?client={client_id}" \
  -H "Authorization: Token $TOKEN"
```

### 5. Emission Records

#### 5.1 List Records
```bash
curl -X GET "http://localhost:8000/api/records/?client={client_id}" \
  -H "Authorization: Token $TOKEN"
```

#### 5.2 Get Dashboard Summary
```bash
curl -X GET "http://localhost:8000/api/records/dashboard_summary/?client={client_id}" \
  -H "Authorization: Token $TOKEN"
```

### 6. File Upload Simulation

```bash
# Create a test CSV file
cat > test_sap.csv << 'EOF'
EBELN,WERKS,MATNR,MAKTX,MENGE,BSTME,BUDAT
PO001,P001,MAT001,Fuel,100,L,20240101
PO002,P001,MAT002,Electricity,200,KWH,20240102
EOF

# Upload file (need to replace with real client_id and data_source_id)
curl -X POST http://localhost:8000/api/ingestion/ingest_sap/ \
  -H "Authorization: Token $TOKEN" \
  -F "file=@test_sap.csv" \
  -F "client_id={client_id}" \
  -F "data_source_id={data_source_id}"
```

---

## Frontend Testing

### 1. Authentication UI Test
- [ ] Navigate to http://localhost:3000
- [ ] See Login form
- [ ] Email field has id="email" and name="email"
- [ ] Password field has id="password" and name="password"
- [ ] Click Sign In
- [ ] Redirected to Dashboard
- [ ] Token stored in localStorage

### 2. Client Selection UI Test
- [ ] See Sidebar with client list
- [ ] Click a client to select
- [ ] Client name appears in navbar
- [ ] DataIngestion page shows selected client

### 3. Data Ingestion UI Test
- [ ] Navigate to "Upload Data" page
- [ ] See form with proper structure:
  - [ ] Data Source Type section (radio buttons)
    - [ ] SAP option has id="source-sap"
    - [ ] Utility option has id="source-utility"
    - [ ] Travel option has id="source-travel"
  - [ ] Data Source Instance dropdown
    - [ ] Has id="dataSourceInstance"
    - [ ] Has name="dataSourceInstance"
  - [ ] File input
    - [ ] Has id="csvFile"
    - [ ] Has name="csvFile"
    - [ ] Accepts .csv and .xlsx

### 4. File Upload Test
- [ ] Select SAP data source type
- [ ] Select data source instance from dropdown
- [ ] Choose a CSV file
- [ ] Click "Upload & Ingest Data"
- [ ] See loading state
- [ ] See success message with job details
- [ ] Data appears in Records list

### 5. Records Review Test
- [ ] Navigate to "Review Records" page
- [ ] See list of records
- [ ] Can click on a record to see details
- [ ] Can approve/reject/flag records
- [ ] Actions update record status

### 6. Dashboard Test
- [ ] Navigate to Dashboard
- [ ] See summary statistics
- [ ] See breakdown by scope
- [ ] Numbers match records in the system

---

## Error Handling Tests

### Test: Missing Authentication
```bash
curl http://localhost:8000/api/clients/
# Expected: 401 Unauthorized - "Authentication credentials were not provided."
```

### Test: Invalid Token
```bash
curl -X GET http://localhost:8000/api/clients/ \
  -H "Authorization: Token invalid_token"
# Expected: 401 Unauthorized
```

### Test: Missing Required Fields in Upload
```bash
curl -X POST http://localhost:8000/api/ingestion/ingest_sap/ \
  -H "Authorization: Token $TOKEN" \
  -F "file=@test_sap.csv"
# Expected: 400 Bad Request - "Missing required fields"
```

### Test: Invalid CSV Format
```bash
# Create invalid CSV
echo "invalid,data,format" > bad.csv

curl -X POST http://localhost:8000/api/ingestion/ingest_sap/ \
  -H "Authorization: Token $TOKEN" \
  -F "file=@bad.csv" \
  -F "client_id={client_id}" \
  -F "data_source_id={data_source_id}"
# Expected: 400 Bad Request with parsing error details
```

---

## Browser Console Checks

### Check Storage
```javascript
// In browser console:
localStorage.getItem('authToken')
// Should show: Token abc123def456...
```

### Check Network Requests
DevTools > Network tab > XHR filter:
- [ ] POST /api/auth/login/ → 200 OK
- [ ] GET /api/clients/ → 200 OK
- [ ] GET /api/data-sources/ → 200 OK
- [ ] POST /api/ingestion/ingest_sap/ → 201 CREATED

### Check Headers
Click on any API request:
- [ ] Request Headers include: `Authorization: Token ...`
- [ ] Response Headers include: `Access-Control-Allow-Origin: http://localhost:3000`

---

## Performance Checks

- [ ] Initial load < 3 seconds
- [ ] Login completes < 1 second
- [ ] Client list loads < 1 second
- [ ] File upload starts immediately
- [ ] 1000+ records load with pagination

---

## Deployed Environment Testing

### Render Backend

```bash
# Test health
curl https://breathe-esg-project-9if8.onrender.com/

# Test auth
curl -X POST https://breathe-esg-project-9if8.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@breatheesg.com","password":"demo1234"}'
```

### Vercel Frontend

- [ ] Load https://breathe-esg-project-ochre.vercel.app
- [ ] Login works
- [ ] API calls go to correct backend URL
- [ ] File upload works end-to-end

---

## Database Verification

### SQLite (Local)
```bash
# Check if database exists
ls -la backend/db.sqlite3

# Check tables
sqlite3 backend/db.sqlite3 ".tables"

# Expected tables: core_client, core_datasource, core_emissionrecord, auth_user, authtoken_token, etc.
```

### PostgreSQL (Deployed)
```bash
# Connect to database
psql -h <host> -U <user> -d <db_name>

# List tables
\dt

# Check users
SELECT * FROM auth_user;

# Check clients
SELECT * FROM core_client;
```

---

## Troubleshooting Quick Fixes

### 403 Errors During Testing
1. Check token is valid: `curl http://localhost:8000/api/auth/login/`
2. Verify token format: `Authorization: Token <key>` (not "Bearer")
3. Check CORS headers in response
4. Clear localStorage and re-login

### Form Not Submitting
1. Check console for JavaScript errors
2. Verify all required fields have values
3. Check file is selected and not too large
4. Verify browser allows multipart/form-data

### File Upload Fails
1. Check CSV format matches expected columns
2. Verify file size < 10MB
3. Check backend logs for parsing errors
4. Try with provided sample data first

### Data Not Appearing After Upload
1. Check job status endpoint: `GET /api/ingestion-jobs/`
2. Review error logs in job details
3. Verify client_id and data_source_id are correct
4. Check database for created records

---

## Final Sign-Off

- [ ] All API endpoints respond correctly
- [ ] Authentication flow works end-to-end
- [ ] File uploads process successfully
- [ ] Records display in UI
- [ ] Approval/rejection workflows function
- [ ] No console errors or warnings
- [ ] CORS working properly
- [ ] Database persists data correctly
- [ ] Both local and deployed versions work

**Ready for Production:** ✅
