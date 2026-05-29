# Quick Start Guide

Get the Breathe ESG platform running in 5 minutes.

## Option 1: Docker Compose (Easiest)

### Prerequisites
- Docker & Docker Compose installed
- 5 GB free disk space

### Steps

1. **Clone repository**:
   ```bash
   git clone https://github.com/yourusername/Breathe_ESG_Project.git
   cd Breathe_ESG_Project
   ```

2. **Start services**:
   ```bash
   docker-compose up
   ```
   
   This will:
   - Start PostgreSQL database
   - Start Redis cache
   - Build and start Django backend (port 8000)
   - Build and start React frontend (port 3000)

3. **Initialize database** (in new terminal):
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access application**:
   - **Dashboard**: http://localhost:3000
   - **API Docs**: http://localhost:8000/api/docs
   - **Admin Panel**: http://localhost:8000/admin

---

## Option 2: Local Development (More Control)

### Backend

1. **Setup Python environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure database**:
   ```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your database credentials.
# For SQLite quick testing:
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=backend/db.sqlite3

   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Start server**:
   ```bash
   python manage.py runserver
   ```

### Frontend

1. **Setup Node environment** (in new terminal):
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL** (optional):
   ```bash
   # Create .env file
   echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
   ```

3. **Start dev server**:
   ```bash
   npm start
   ```

---

## First Time Setup

Once services are running:

### 1. Create Organization

**Via Django Admin**:
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Click "Clients" → "Add Client"
4. Fill in:
   - Name: "Demo Company"
   - Legal Entity ID: "12345"
   - Country: "US"
   - Fiscal Year Start: "2024-01-01"
5. Save

**Or via API**:
```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your_token>" \
  -d '{
    "name": "Demo Company",
    "legal_entity_id": "12345",
    "country": "US",
    "fiscal_year_start": "2024-01-01"
  }'
```

### 2. Register Data Sources

Create a source for each data type:

```bash
# SAP Source
curl -X POST http://localhost:8000/api/data-sources/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your_token>" \
  -d '{
    "client": "<client_id>",
    "source_type": "sap",
    "name": "SAP ERP Production",
    "configuration": {}
  }'

# Utility Source
curl -X POST http://localhost:8000/api/data-sources/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your_token>" \
  -d '{
    "client": "<client_id>",
    "source_type": "utility",
    "name": "Utility Portal",
    "configuration": {}
  }'

# Travel Source
curl -X POST http://localhost:8000/api/data-sources/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <your_token>" \
  -d '{
    "client": "<client_id>",
    "source_type": "travel",
    "name": "Concur/Navan",
    "configuration": {}
  }'
```

### 3. Upload Sample Data

1. Download sample CSV files from [docs/SAMPLE_DATA.md](SAMPLE_DATA.md)
2. Go to http://localhost:3000
3. Login (demo user: analyst@breatheesg.com / demo1234)
4. Click "Upload Data"
5. Select data source type and upload CSV
6. System processes and creates records

### 4. Review Records

1. Go to "Review Records" tab
2. Filter by status/scope
3. Click record to view details
4. Click "Approve" or "Flag for Review"

---

## Common Commands

### Backend

```bash
# Create new migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Generate fixture (backup data)
python manage.py dumpdata > data.json

# Load fixture
python manage.py loaddata data.json
```

### Frontend

```bash
# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test

# Format code
npm run format
```

### Docker

```bash
# View logs
docker-compose logs -f backend

# Run command in container
docker-compose exec backend python manage.py migrate

# Stop services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

---

## Test Data

Create test records via API:

```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst","password":"demo1234"}' | jq -r '.token')

# Upload SAP data
curl -X POST http://localhost:8000/api/ingestion/ingest-sap/ \
  -H "Authorization: Token $TOKEN" \
  -F "file=@sap_sample.csv" \
  -F "client_id=<client_id>" \
  -F "data_source_id=<source_id>"
```

---

## Troubleshooting

### "Connection refused" to database
- Check PostgreSQL is running: `docker ps` should show postgres container
- Check credentials in `.env` match database config
- Or switch to SQLite: `DB_ENGINE=django.db.backends.sqlite3`

### "Migrations pending" error
```bash
python manage.py migrate
```

### CORS errors in browser console
- Check `CORS_ALLOWED_ORIGINS` in `backend/config/settings.py`
- Should include your frontend URL (http://localhost:3000)

### Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001
# Update REACT_APP_API_URL to http://localhost:8001/api
```

### Port 3000 already in use
```bash
PORT=3001 npm start
```

### Database not initialized
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

---

## Next Steps

1. **Read documentation**:
   - [Data Model](MODEL.md) - Understanding the schema
   - [Design Decisions](DECISIONS.md) - Why we built this way
   - [Source Formats](SOURCES.md) - Deep dive into data sources

2. **Explore API**:
   - OpenAPI docs: http://localhost:8000/api/docs
   - Try uploading sample data
   - Review and approve records

3. **Deploy**:
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for Render/Railway/Fly.io setup
   - Configure production environment variables
   - Set up automated backups

4. **Extend**:
   - Add more data sources
   - Integrate real SAP/Concur APIs
   - Build custom reports

---

## Support

- **API Documentation**: http://localhost:8000/api/docs
- **Django Admin**: http://localhost:8000/admin
- **Source Code**: Check `docs/` directory for detailed documentation
- **Issues**: Open GitHub issue with error logs and steps to reproduce

Happy emissions tracking! 🌱
