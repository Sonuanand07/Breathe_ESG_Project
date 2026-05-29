# Testing Guide for Breathe ESG

Complete guide for testing the application locally and in production.

---

## Part 1: Local Testing Setup

### 1.1 Full Local Development Environment

#### Quick Start (All Services)

```bash
# Start everything with docker-compose
docker-compose up -d

# Wait 15 seconds for services to be healthy
sleep 15

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/api
# - Admin: http://localhost:8000/admin
# - API Docs: http://localhost:8000/api/docs
```

#### Manual Setup (Without Docker)

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm install
npm start

# Terminal 3: (Optional) Redis for Celery
redis-server
```

---

## Part 2: Backend Testing

### 2.1 Test Database Connection

```bash
cd backend
python manage.py shell
```

```python
# Test Django ORM
from django.db import connection
cursor = connection.cursor()
print("Database connected successfully")

# Test models
from apps.core.models import Client
print(f"Clients in database: {Client.objects.count()}")

# Create test client
client = Client.objects.create(
    name="Test Company",
    legal_entity_id="TEST-001"
)
print(f"Created client: {client.name}")

# Verify it's saved
print(f"Total clients: {Client.objects.count()}")
```

### 2.2 Test API Endpoints

```bash
# Test using curl

# 1. Get API root
curl http://localhost:8000/api/

# 2. Get API documentation
curl http://localhost:8000/api/docs

# 3. Create client
curl -X POST http://localhost:8000/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "legal_entity_id": "TEST-001"
  }'

# 4. List clients
curl http://localhost:8000/api/clients/

# 5. Create data source
curl -X POST http://localhost:8000/api/data-sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "name": "SAP Instance",
    "source_type": "sap",
    "location": "SAP ECC Production"
  }'

# 6. List data sources
curl http://localhost:8000/api/data-sources/
```

### 2.3 Test Admin Panel

1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Test CRUD operations:
   - [ ] Create new Client
   - [ ] Create new DataSource
   - [ ] View EmissionRecords
   - [ ] View AuditLogs

### 2.4 Test Data Ingestion

#### SAP CSV Upload

Create `test_sap.csv`:
```csv
EBELN,EBELP,WERKS,MATNR,MAKTX,BSTME,MENGE,BUDAT,LIFNR,NAME1
4600012345,00010,1000,MAT-001,DIESEL FUEL,L,1500,20240115,200005,ABC Oil
4600012346,00020,1000,MAT-002,PETROL,L,500,20240116,200005,ABC Oil
```

Upload via API:
```bash
curl -X POST http://localhost:8000/api/ingestion/ingest-sap/ \
  -F "client_id=1" \
  -F "data_source_id=1" \
  -F "file=@test_sap.csv"
```

#### Utility CSV Upload

Create `test_utility.csv`:
```csv
meter_id,facility_name,utility_provider,billing_period_start,billing_period_end,consumption_kwh,tariff_name
MTR-001,SF HQ,PG&E,2024-01-12,2024-02-16,2595,A-10
MTR-002,NYC Office,ConEd,2024-01-15,2024-02-12,1850,C-1
```

Upload via API:
```bash
curl -X POST http://localhost:8000/api/ingestion/ingest-utility/ \
  -F "client_id=1" \
  -F "data_source_id=2" \
  -F "file=@test_utility.csv"
```

#### Travel CSV Upload

Create `test_travel.csv`:
```csv
trip_id,travel_mode,departure_airport,arrival_airport,seat_class,distance_km,number_of_nights,expense_date
TRIP-001,flight,SFO,JFK,economy,4160,,2024-01-15
TRIP-002,hotel,,,,,3,2024-01-16
```

Upload via API:
```bash
curl -X POST http://localhost:8000/api/ingestion/ingest-travel/ \
  -F "client_id=1" \
  -F "data_source_id=3" \
  -F "file=@test_travel.csv"
```

### 2.5 Test Emission Records

```bash
# List all records
curl http://localhost:8000/api/records/

# Filter by scope
curl http://localhost:8000/api/records/?scope=1

# Filter by status
curl http://localhost:8000/api/records/?status=pending

# Get single record
curl http://localhost:8000/api/records/1/

# Approve record
curl -X POST http://localhost:8000/api/records/1/approve/ \
  -H "Content-Type: application/json" \
  -d '{"notes": "Approved by analyst"}'

# Reject record
curl -X POST http://localhost:8000/api/records/1/reject/ \
  -H "Content-Type: application/json" \
  -d '{"notes": "Data inconsistency"}'

# Flag record
curl -X POST http://localhost:8000/api/records/1/flag/ \
  -H "Content-Type: application/json" \
  -d '{"notes": "Need further investigation"}'

# Get dashboard summary
curl http://localhost:8000/api/records/dashboard_summary/
```

### 2.6 Test Audit Trail

```bash
# View audit logs
curl http://localhost:8000/api/audit-logs/

# Filter by record
curl http://localhost:8000/api/audit-logs/?record_id=1

# View complete audit history for record
curl http://localhost:8000/api/audit-logs/?record_id=1&ordering=-created_at
```

---

## Part 3: Frontend Testing

### 3.1 Test Application Startup

```bash
cd frontend
npm start
```

Expected: React app opens at http://localhost:3000

### 3.2 Test Login Flow

1. Click "Login" button
2. Enter credentials:
   - Email: admin@example.com
   - Password: (your superuser password)
3. Verify dashboard loads

### 3.3 Test Dashboard Components

- [ ] **Summary Stats**: Total CO2e, Pending Records, Approval Rate
- [ ] **Pending Records Table**: Shows pending records with filters
- [ ] **Record Details Modal**: Click record → view full details
- [ ] **Approval Workflow**: Approve/Reject/Flag buttons work

### 3.4 Test File Upload

1. Navigate to "Upload Data" section
2. Select source type (SAP/Utility/Travel)
3. Choose CSV file
4. Click upload
5. Verify success message
6. Check records appear in dashboard

### 3.5 Test Filtering

In records table:
- [ ] Filter by Scope (1, 2, 3)
- [ ] Filter by Status (pending, approved, rejected, flagged)
- [ ] Filter by Category (fuel, electricity, flight, hotel, etc.)
- [ ] Filter by Date Range
- [ ] Filter by Quality Score

### 3.6 Test Pagination

- [ ] First page loads
- [ ] Next page works
- [ ] Previous page works
- [ ] Page size selector works (10, 25, 50 per page)

### 3.7 Test Responsive Design

Test on different screen sizes:
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

---

## Part 4: Integration Testing

### 4.1 End-to-End Workflow

```
1. Login to frontend
2. Upload SAP CSV
3. Verify records in dashboard
4. Approve one record
5. Reject another
6. Flag one for review
7. Check audit trail
8. View dashboard statistics
```

### 4.2 Data Integrity Tests

```bash
python manage.py shell
```

```python
from apps.core.models import EmissionRecord, AuditLog

# Verify data saved correctly
record = EmissionRecord.objects.first()
print(f"Quantity: {record.quantity} {record.unit}")
print(f"Normalized Quantity: {record.normalized_quantity} {record.normalized_unit}")
print(f"CO2e: {record.co2e}")
print(f"Scope: {record.scope}")

# Verify audit trail
audits = AuditLog.objects.filter(record=record).order_by('created_at')
for audit in audits:
    print(f"{audit.created_at}: {audit.action} by {audit.user}")
```

### 4.3 Unit Conversion Tests

```python
# Test SAP fuel conversion
from apps.ingestion.parsers import SAP Parser

parser = SAP_Parser()
# Gallons to liters
converted = parser.convert_unit(1, 'gal', 'L')
print(f"1 gallon = {converted} liters (expected ~3.785)")
```

### 4.4 Emission Factor Tests

```python
from apps.ingestion.parsers import EmissionFactors

factors = EmissionFactors()
diesel_factor = factors.get_factor('diesel')
print(f"Diesel: {diesel_factor} kg CO2e/L (expected ~2.68)")
```

---

## Part 5: Load Testing

### 5.1 Create Large Dataset

```bash
cd backend
python manage.py shell
```

```python
from apps.core.models import Client, DataSource, EmissionRecord
from datetime import datetime, timedelta

client = Client.objects.first()
source = DataSource.objects.first()

# Create 1000 records
for i in range(1000):
    EmissionRecord.objects.create(
        client=client,
        source=source,
        source_identifier=f"LOAD-TEST-{i}",
        category="fuel",
        scope="1",
        quantity=100 + i,
        unit="L",
        normalized_quantity=100 + i,
        normalized_unit="L",
        conversion_factor=1.0,
        co2e=268 + (i * 0.1),
        status="pending",
        raw_data={"test": True}
    )
print("Created 1000 records")
```

### 5.2 Performance Testing

```bash
# Test API with many records
time curl http://localhost:8000/api/records/?limit=100

# Test filtering performance
time curl http://localhost:8000/api/records/?scope=1&status=pending

# Check database query performance
python manage.py shell
from django.test.utils import CaptureQueriesContext
from django.db import connection

with CaptureQueriesContext(connection) as ctx:
    from apps.core.models import EmissionRecord
    records = EmissionRecord.objects.select_related('client', 'source')
    list(records[:10])
    
print(f"Number of queries: {len(ctx)}")
for q in ctx:
    print(f"Query: {q['sql'][:100]}...")
```

### 5.3 Frontend Performance

```bash
# Build for production
cd frontend
npm run build

# Serve production build
npx serve -s build

# Test at http://localhost:5000
# Check browser DevTools → Performance tab
```

---

## Part 6: Security Testing

### 6.1 SQL Injection Test

```bash
# Try malicious input (should be safe due to Django ORM)
curl "http://localhost:8000/api/records/?scope=1%20OR%201=1"

# Verify only valid records returned
```

### 6.2 CSRF Protection Test

```bash
# POST without CSRF token (should fail in production)
curl -X POST http://localhost:8000/api/records/ \
  -H "Content-Type: application/json" \
  -d '{"data": "test"}'
```

### 6.3 CORS Test

```bash
# Test CORS headers
curl -i -X OPTIONS http://localhost:8000/api/ \
  -H "Origin: http://localhost:3000"

# Should return Access-Control-Allow-Origin header
```

### 6.4 Authentication Test

```bash
# Try accessing protected endpoint without token
curl http://localhost:8000/api/admin/clients/

# Should return 401 Unauthorized
```

---

## Part 7: Browser Testing

### 7.1 Chrome DevTools Tests

1. Open DevTools (F12)
2. Go to Console tab
3. Check for errors
4. Test Network tab during API calls
5. Check Storage tab for tokens

### 7.2 Lighthouse Audit

1. Open DevTools → Lighthouse
2. Run audit
3. Check scores:
   - Performance: > 90
   - Accessibility: > 90
   - Best Practices: > 90
   - SEO: > 90

### 7.3 Cross-Browser Testing

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Part 8: Production Testing

### 8.1 Verify Deployment

```bash
# Test backend health
curl https://breathe-esg-backend.onrender.com/api/health

# Test frontend loads
curl https://breathe-esg-frontend.vercel.app | grep "<html>"

# Test API connectivity
curl https://breathe-esg-backend.onrender.com/api/docs
```

### 8.2 Test Production Database

```bash
# Connect to production database
psql -U breathe_user -d breathe_esg -h <production-host>

# Verify tables exist
\dt

# Check row counts
SELECT COUNT(*) FROM core_emissionrecord;
```

### 8.3 Test Production API

```bash
# Create test record
curl -X POST https://breathe-esg-backend.onrender.com/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Prod Test","legal_entity_id":"PROD-TEST"}'

# Verify record exists
curl https://breathe-esg-backend.onrender.com/api/clients/
```

### 8.4 Test Production Frontend

1. Open https://breathe-esg-frontend.vercel.app
2. Login with production credentials
3. Upload test data
4. Verify data appears
5. Test approval workflow
6. Check audit trail

---

## Part 9: Automated Testing

### 9.1 Django Tests

```bash
cd backend
python manage.py test
```

### 9.2 Create Test Cases

Create `backend/apps/core/tests.py`:
```python
from django.test import TestCase
from apps.core.models import Client, EmissionRecord

class ClientTestCase(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            name="Test Company",
            legal_entity_id="TEST-001"
        )
    
    def test_client_created(self):
        self.assertEqual(self.client.name, "Test Company")
        self.assertEqual(Client.objects.count(), 1)
```

### 9.3 React Tests

```bash
cd frontend
npm test
```

### 9.4 API Tests with Jest

Create `frontend/src/__tests__/api.test.js`:
```javascript
import { getClients } from '../services/api';

describe('API Client', () => {
  test('getClients returns array', async () => {
    const clients = await getClients();
    expect(Array.isArray(clients)).toBe(true);
  });
});
```

---

## Part 10: Test Checklist

### Backend
- [ ] Database migrations work
- [ ] Models created correctly
- [ ] API endpoints respond
- [ ] Admin panel functional
- [ ] Authentication works
- [ ] File uploads work
- [ ] CSV parsing works
- [ ] Emission calculations correct
- [ ] Audit trail recorded
- [ ] Filtering works
- [ ] Pagination works

### Frontend
- [ ] App loads
- [ ] Login works
- [ ] Dashboard displays
- [ ] File upload works
- [ ] Records display
- [ ] Filtering works
- [ ] Approval workflow works
- [ ] Responsive on mobile
- [ ] No console errors
- [ ] API calls successful

### Integration
- [ ] End-to-end workflow complete
- [ ] Data integrity maintained
- [ ] Audit trail accurate
- [ ] Performance acceptable
- [ ] Security measures working

### Deployment
- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Database connection works
- [ ] Environment variables correct
- [ ] HTTPS working
- [ ] CORS configured
- [ ] Backups enabled

---

## Test Data Files

### SAP Test File (`test_sap.csv`)
```csv
EBELN,EBELP,WERKS,MATNR,MAKTX,BSTME,MENGE,BUDAT,LIFNR,NAME1
4600012345,00010,1000,MAT-001,DIESEL FUEL,L,1500,20240115,200005,ABC Oil
4600012346,00020,1000,MAT-002,PETROL,L,500,20240116,200005,ABC Oil
4600012347,00030,1000,MAT-003,JET FUEL,L,2000,20240117,200006,XYZ Aviation
```

### Utility Test File (`test_utility.csv`)
```csv
meter_id,facility_name,utility_provider,billing_period_start,billing_period_end,consumption_kwh,tariff_name
MTR-001,SF HQ,PG&E,2024-01-12,2024-02-16,2595,A-10
MTR-002,NYC Office,ConEd,2024-01-15,2024-02-12,1850,C-1
MTR-003,LA Warehouse,Edison,2024-01-10,2024-02-10,5000,TOU-4
```

### Travel Test File (`test_travel.csv`)
```csv
trip_id,travel_mode,departure_airport,arrival_airport,seat_class,distance_km,number_of_nights,expense_date
TRIP-001,flight,SFO,JFK,economy,4160,,2024-01-15
TRIP-002,hotel,,,,,3,2024-01-16
TRIP-003,flight,LAS,ORD,business,2200,,2024-01-17
TRIP-004,ground,,,,,0,2024-01-17
```

---

## Summary

| Test Type | Frequency | Time | Coverage |
|-----------|-----------|------|----------|
| Unit Tests | Every commit | < 1 min | 80%+ |
| Integration Tests | Every PR | 5 min | 90%+ |
| Manual Testing | Before deploy | 30 min | 100% |
| Load Testing | Monthly | 15 min | Peak usage |
| Security Scan | Weekly | 10 min | All inputs |
| Performance | Monthly | 20 min | All features |

---

## Testing Commands Quick Reference

```bash
# Local backend
python manage.py runserver

# Local frontend
npm start

# Run all tests
python manage.py test

# Docker stack
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Create test data
python manage.py shell < create_test_data.py

# Production API
curl https://your-backend.onrender.com/api/docs

# Database check
python manage.py dbshell
```

---

**All tests passing? You're ready to deploy!**
