# Database Setup Guide for Breathe ESG

Complete guide for setting up SQLite (local testing) and PostgreSQL (production) databases.

---

## Quick Start

### Option A: SQLite (Recommended for Local Development)
```bash
# 1. Navigate to backend
cd backend

# 2. Copy environment file
cp .env.example .env

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

### Option B: PostgreSQL with Docker (Recommended for Production-like Testing)
```bash
# Start PostgreSQL and other services
docker-compose up -d

# Wait for services to be healthy (10-15 seconds)
docker-compose ps

# Run migrations in backend container
docker-compose exec backend python manage.py migrate

# Create superuser in backend container
docker-compose exec backend python manage.py createsuperuser

# View logs
docker-compose logs -f backend
```

---

## Detailed Setup Instructions

## Part 1: SQLite Setup (Local Development)

### 1.1 When to Use SQLite
- ✅ **Perfect for**: Local development, quick testing, prototyping
- ✅ **Advantages**: No separate database server, single file, zero configuration
- ✅ **Limitations**: Not suitable for production or concurrent access

### 1.2 SQLite Configuration

**File**: `backend/.env`
```bash
# SQLite Configuration (Default)
DEBUG=True
SECRET_KEY=local-dev-secret-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,example.com

# Database: SQLite
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=backend/db.sqlite3

# Optional
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 1.3 Complete SQLite Setup Steps

#### Step 1: Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed Django==4.2 djangorestframework==3.14 psycopg2-binary==2.9 ...
```

#### Step 3: Create .env File
```bash
cp .env.example .env
```

Verify `DB_ENGINE` is set to `django.db.backends.sqlite3`

#### Step 4: Run Migrations
```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, ingestion, sessions
Running migrations:
  Applying core.0001_initial... OK
  Applying auth.0002_alter_permission_options... OK
  ...
```

This creates `backend/db.sqlite3`

#### Step 5: Create Superuser Account
```bash
python manage.py createsuperuser
```

Follow prompts:
```
Username: admin
Email: admin@example.com
Password: (enter secure password)
Password (again): (confirm)
Superuser created successfully.
```

#### Step 6: Run Development Server
```bash
python manage.py runserver
```

Expected output:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 29, 2026 - 10:00:00
Django version 4.2, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

#### Step 7: Access the Application
- **Django Admin**: http://127.0.0.1:8000/admin (use superuser credentials)
- **API Documentation**: http://127.0.0.1:8000/api/docs
- **API Root**: http://127.0.0.1:8000/api

#### Step 8: Verify Database

In Python shell:
```bash
python manage.py shell
```

```python
from django.core.management import call_command
from apps.core.models import Client

# Check if tables exist
print("Database tables created successfully")

# Create test client
client = Client.objects.create(
    name="Test Company",
    legal_entity_id="TEST-001"
)
print(f"Test client created: {client.name}")
```

### 1.4 Common SQLite Issues and Solutions

#### Issue 1: "sqlite3.OperationalError: database is locked"
**Cause**: Multiple processes accessing database simultaneously
**Solution**:
```bash
# Kill any existing Django processes
# On Windows:
taskkill /IM python.exe /F

# On macOS/Linux:
pkill -f "python manage.py runserver"

# Restart server
python manage.py runserver
```

#### Issue 2: "ModuleNotFoundError: No module named 'apps.core'"
**Cause**: Not in correct directory
**Solution**:
```bash
cd backend
python manage.py migrate
```

#### Issue 3: Database file too large
**Cause**: Accumulated test data
**Solution**: Delete and recreate
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### 1.5 SQLite Database File Locations

```
backend/
├── db.sqlite3          # Main database file (auto-created after migrate)
├── .env                # Configuration file
├── manage.py
└── config/
    └── settings.py
```

**File Size**: Typical development database starts at ~100 KB, grows as you add records

### 1.6 SQLite Performance Tips

For development, SQLite is sufficient, but keep in mind:
- ⚠️ Not recommended for >100 concurrent users
- ⚠️ Slower than PostgreSQL for complex queries
- ⚠️ File-locked during writes (few milliseconds)

---

## Part 2: PostgreSQL Setup (Production & Testing)

### 2.1 When to Use PostgreSQL
- ✅ **Perfect for**: Production deployments, testing concurrent access
- ✅ **Advantages**: Robust, scalable, ACID transactions, advanced features
- ✅ **Limitations**: Requires separate server installation

### 2.2 Prerequisites

#### Option A: PostgreSQL Installed Locally

**macOS** (Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows** (Installer):
Download from https://www.postgresql.org/download/windows/

**Linux** (Ubuntu/Debian):
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Option B: PostgreSQL via Docker (Recommended)
```bash
docker run -d \
  --name postgres15 \
  -e POSTGRES_DB=breathe_esg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

### 2.3 PostgreSQL Configuration

**File**: `backend/.env`
```bash
# PostgreSQL Configuration
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database: PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=breathe_esg
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Optional
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 2.4 Complete PostgreSQL Setup Steps (Local)

#### Step 1: Verify PostgreSQL is Running

**macOS/Linux**:
```bash
sudo systemctl status postgresql
```

**Windows**: Check Services for "postgresql" or use pgAdmin

**Docker**:
```bash
docker ps  # Should show postgres container running
```

#### Step 2: Create Database and User

**Option A: Using psql** (command line)
```bash
psql -U postgres -c "CREATE DATABASE breathe_esg;"
psql -U postgres -c "CREATE USER breathe_user WITH PASSWORD 'secure_password';"
psql -U postgres -c "ALTER ROLE breathe_user SET client_encoding TO 'utf8';"
psql -U postgres -c "ALTER ROLE breathe_user SET default_transaction_isolation TO 'read committed';"
psql -U postgres -c "ALTER ROLE breathe_user SET default_transaction_deferrable TO on;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE breathe_esg TO breathe_user;"
```

**Option B: Using pgAdmin** (GUI)
1. Open pgAdmin (http://localhost:5050 if using Docker)
2. Right-click "Databases" → "Create" → "Database"
3. Name: `breathe_esg`
4. Owner: postgres
5. Create

#### Step 3: Update .env File
```bash
cp .env.example .env
```

Edit `backend/.env`:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=breathe_esg
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

#### Step 4: Install Python Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 5: Run Migrations
```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, ingestion, sessions
Running migrations:
  Applying core.0001_initial... OK
  ...
```

#### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

#### Step 7: Run Development Server
```bash
python manage.py runserver
```

#### Step 8: Verify Connection

In Python shell:
```bash
python manage.py shell
```

```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

# Output: ('PostgreSQL 15.2 on x86_64-pc-linux-gnu...')
```

### 2.5 Common PostgreSQL Issues and Solutions

#### Issue 1: "connection refused" on port 5432
**Cause**: PostgreSQL not running
**Solution**:
```bash
# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql

# Docker
docker start postgres15
```

#### Issue 2: "FATAL: Ident authentication failed for user 'postgres'"
**Cause**: Authentication method mismatch
**Solution**: Edit `pg_hba.conf`
```bash
# Find pg_hba.conf location
sudo -u postgres psql -c "SHOW hba_file;"

# Edit file, change "ident" to "md5" or "scram-sha-256"
# Then restart PostgreSQL
```

#### Issue 3: "does not exist" error for database
**Cause**: Database not created
**Solution**:
```bash
psql -U postgres -c "CREATE DATABASE breathe_esg;"
```

#### Issue 4: "FATAL: role 'postgres' does not exist"
**Cause**: PostgreSQL not initialized
**Solution**:
```bash
# macOS
brew reinstall postgresql@15

# Linux
sudo apt-get install --reinstall postgresql

# Docker
docker rm postgres15
# Recreate container with proper initialization
```

### 2.6 PostgreSQL Performance Features

PostgreSQL provides advanced features useful for production:

```sql
-- Create index for common queries
CREATE INDEX idx_emission_records_client_id ON core_emissionrecord(client_id);
CREATE INDEX idx_emission_records_scope ON core_emissionrecord(scope);
CREATE INDEX idx_emission_records_status ON core_emissionrecord(status);

-- View query performance
EXPLAIN ANALYZE
SELECT * FROM core_emissionrecord WHERE scope = '1' AND status = 'approved';
```

### 2.7 PostgreSQL Backup and Restore

#### Backup Database
```bash
pg_dump -U postgres breathe_esg > backup.sql
```

#### Restore Database
```bash
psql -U postgres breathe_esg < backup.sql
```

#### Docker Backup
```bash
docker exec postgres15 pg_dump -U postgres breathe_esg > backup.sql
```

---

## Part 3: Docker Compose (Complete Stack)

### 3.1 Quick Start with Docker

```bash
# Start all services (PostgreSQL, Redis, Django, React)
docker-compose up -d

# Wait 15 seconds for services to be ready
sleep 15

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Check logs
docker-compose logs -f
```

### 3.2 Services in Docker Compose

**postgres:15-alpine**
- Port: 5432
- User: postgres
- Password: postgres
- Database: breathe_esg
- Volume: postgres_data

**redis:7-alpine**
- Port: 6379
- Purpose: Celery message broker

**backend**
- Port: 8000
- API: http://localhost:8000/api
- Admin: http://localhost:8000/admin

**frontend**
- Port: 3000
- App: http://localhost:3000

### 3.3 Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python manage.py shell

# View running services
docker-compose ps

# Remove volumes (caution - deletes data)
docker-compose down -v
```

### 3.4 Verify Docker Stack

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U postgres -d breathe_esg -c "\dt"

# Check Redis
docker-compose exec redis redis-cli ping

# Check backend health
curl http://localhost:8000/api/

# Check frontend
curl http://localhost:3000
```

---

## Part 4: Database Features & Extensions

### 4.1 PostgreSQL Full-Text Search (Optional)

For advanced search across records:

```python
# In apps/core/models.py
from django.contrib.postgres.search import SearchVectorField

class EmissionRecord(models.Model):
    # ... other fields ...
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
        ]
```

Then enable in Django:

```bash
python manage.py migrate
```

### 4.2 PostgreSQL JSON Fields (Already Implemented)

```python
# Already in models for storing raw data
class SAPRecord(models.Model):
    raw_data = models.JSONField(default=dict)
```

### 4.3 PostgreSQL Triggers (Optional for Audit Trail)

```sql
-- Auto-update timestamp
CREATE TRIGGER update_timestamp
BEFORE UPDATE ON core_emissionrecord
FOR EACH ROW
SET new.updated_at = NOW();
```

---

## Part 5: Environment Variables Reference

### Complete .env Template

```bash
# ==================== DJANGO ====================
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
FRONTEND_URL=http://localhost:3000

# ==================== DATABASE ====================
# SQLite (Local Development)
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=backend/db.sqlite3

# PostgreSQL (Production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=breathe_esg
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# ==================== CORS & SECURITY ====================
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# ==================== CELERY (Optional) ====================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_ACCEPT_CONTENT=json

# ==================== AWS S3 (Optional) ====================
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_STORAGE_BUCKET_NAME=your-bucket
# AWS_S3_REGION_NAME=us-east-1

# ==================== EMAIL (Optional) ====================
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# ==================== LOGGING ====================
LOG_LEVEL=INFO
```

---

## Part 6: Troubleshooting Checklist

### Database Connection Issues

- [ ] Database server is running (`docker-compose ps` or `systemctl status postgresql`)
- [ ] Correct credentials in `.env` file
- [ ] Database exists (`psql -l` for PostgreSQL)
- [ ] Port is correct (default: 5432)
- [ ] Firewall allows connection (if remote server)

### Migration Issues

- [ ] Fresh virtual environment (`python -m venv venv` and `pip install -r requirements.txt`)
- [ ] Correct database engine in `.env`
- [ ] No conflicting database schema
- [ ] Python 3.10+

### Django Shell Test

```bash
python manage.py shell
```

```python
from django.db import connection
print(f"Connected to: {connection.settings_dict['ENGINE']}")

from apps.core.models import Client
print(f"Clients in database: {Client.objects.count()}")
```

---

## Part 7: Production Deployment Considerations

### Before Going Live

1. **Security**
   - [ ] Change `SECRET_KEY` in production
   - [ ] Set `DEBUG=False`
   - [ ] Use environment variables for credentials
   - [ ] Enable HTTPS only
   - [ ] Configure firewall rules

2. **Database**
   - [ ] Use managed PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database)
   - [ ] Enable automated backups
   - [ ] Set up read replicas for scaling
   - [ ] Configure connection pooling

3. **Performance**
   - [ ] Add database indexes on foreign keys
   - [ ] Configure query caching (Redis)
   - [ ] Set up CDN for static files
   - [ ] Enable gzip compression

4. **Monitoring**
   - [ ] Set up database monitoring
   - [ ] Track slow queries
   - [ ] Monitor connection pool
   - [ ] Alert on high CPU/memory

---

## Summary Table

| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| Setup Time | < 1 minute | 5 minutes |
| Concurrent Users | 1-2 | 100+ |
| Production Ready | ❌ | ✅ |
| Backup | Easy | Automated |
| Scaling | ❌ | ✅ |
| Recommended For | Development | Production |
| Cost | Free | Free (self-hosted) |

---

## Next Steps

1. **Choose your database**: SQLite for quick local testing, PostgreSQL for production
2. **Follow the steps above** for your chosen database
3. **Run migrations** to create tables
4. **Create superuser** for admin access
5. **Start the server** and access at http://localhost:8000
6. **Upload sample data** via API or admin panel
7. **Test the dashboard** at http://localhost:3000

**Need Help?** Check the logs:
```bash
python manage.py runserver 2>&1 | tee debug.log
```

---

## Additional Resources

- [Django Database Documentation](https://docs.djangoproject.com/en/4.2/ref/databases/)
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [SQLite Official Documentation](https://www.sqlite.org/docs.html)
- [Docker PostgreSQL Image](https://hub.docker.com/_/postgres)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
