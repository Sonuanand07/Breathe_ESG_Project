# Credentials & Security Guide

Complete guide for managing credentials and security in Breathe ESG platform.

---

## Important Security Notice

⚠️ **NEVER commit `.env` file or credentials to GitHub**
⚠️ **NEVER share SECRET_KEY, database passwords, or API keys**
⚠️ **Always use environment variables in production**

---

## Part 1: Local Development Credentials

### 1.1 Development .env File

Create `backend/.env` (do not commit):

```bash
# ============================================================
# BREATHE ESG - LOCAL DEVELOPMENT CONFIGURATION
# ============================================================
# IMPORTANT: This file should NOT be committed to version control
# See .env.example for template

# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-local-dev-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,127.0.0.1:3000,localhost:3000

# Database (SQLite for local)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=backend/db.sqlite3

# Frontend
FRONTEND_URL=http://localhost:3000

# Redis (optional, for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 1.2 Development Superuser Credentials

Create using:
```bash
python manage.py createsuperuser
```

**Recommended for testing**:
```
Username: admin
Email: admin@example.com
Password: admin123  # ONLY for local testing
```

**Access**: http://localhost:8000/admin

---

## Part 2: Production Credentials

### 2.1 Generate Secure Credentials

#### SECRET_KEY (Django)
```bash
# Generate random secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Output:
```
'jv%_x5*+yb@w^+h=!tz3$3x2$_)l)kk#z2&5#$w=t&@0@$c!l'
```

#### Password (Database)
```bash
# Generate random password
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Output:
```
'R8pM2vL9kQ4wX_sJ1nB5cD3fG7hJ9mP0'
```

#### JWT Secret (if using JWT)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Output:
```
'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0'
```

### 2.2 Production Environment (Render)

Use these credentials in Render dashboard:

```bash
# ============================================================
# PRODUCTION - RENDER ENVIRONMENT VARIABLES
# ============================================================

# Django
DEBUG=False
SECRET_KEY=<paste-generated-key-from-section-2.1>
ALLOWED_HOSTS=breathe-esg-backend.onrender.com,yourdomain.com

# Database (PostgreSQL on Render)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=breathe_esg
DB_USER=breathe_user
DB_PASSWORD=<paste-generated-password>
DB_HOST=dpg-xxxxx-xxxxx.postgres.render.com
DB_PORT=5432

# Frontend
FRONTEND_URL=https://your-vercel-frontend.vercel.app
CORS_ALLOWED_ORIGINS=https://your-vercel-frontend.vercel.app

# Security
CSRF_TRUSTED_ORIGINS=https://breathe-esg-backend.onrender.com

# Logging
LOG_LEVEL=INFO
```

### 2.3 Production Superuser (Render)

```bash
# Option 1: Via Render Shell
# Dashboard → Services → Your Backend → Shell
python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@yourdomain.com
# Password: <strong-password>

# Option 2: Via Django Admin Page
# After logging in to admin, create users there
```

Access: https://breathe-esg-backend.onrender.com/admin

---

## Part 3: API Credentials

### 3.1 Generate API Token

```bash
# Create token for API authentication
python manage.py shell
```

```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Get or create user
user = User.objects.get(username='admin')

# Generate token
token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key}")
```

Example output:
```
Token: 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 3.2 Use API Token

Include token in API requests:

```bash
curl -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  https://breathe-esg-backend.onrender.com/api/clients/
```

Or in React:
```javascript
const response = await fetch('/api/clients/', {
  headers: {
    'Authorization': 'Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
  }
});
```

### 3.3 Rotate Token

```bash
python manage.py shell
```

```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='admin')
# Delete old token
Token.objects.filter(user=user).delete()
# Create new token
token = Token.objects.create(user=user)
print(f"New Token: {token.key}")
```

---

## Part 4: Third-Party API Keys (Optional)

### 4.1 AWS S3 (for file uploads)

```bash
# Generate AWS credentials
# 1. Go to AWS Console → IAM
# 2. Create new user
# 3. Attach S3 policy
# 4. Create access key

# Add to .env:
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=breathe-esg-bucket
AWS_S3_REGION_NAME=us-east-1
```

### 4.2 SendGrid Email (for notifications)

```bash
# Generate SendGrid API key
# 1. Go to SendGrid dashboard
# 2. API Keys → Create API Key

# Add to .env:
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
EMAIL_FROM=noreply@example.com
```

### 4.3 OAuth (if integrating with other services)

```bash
# Example: Google OAuth
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx

# Example: GitHub OAuth
GITHUB_CLIENT_ID=xxxxx
GITHUB_CLIENT_SECRET=xxxxx
```

---

## Part 5: Database Credentials

### 5.1 PostgreSQL Connection

**Local Development**:
```
Host: localhost
Port: 5432
Username: postgres
Password: postgres
Database: breathe_esg
```

**Production (Render)**:
```
Host: dpg-xxxxx-xxxxx.postgres.render.com
Port: 5432
Username: breathe_user
Password: <generated-password>
Database: breathe_esg
Connection String: postgresql://breathe_user:password@host:5432/breathe_esg
```

### 5.2 Connect via psql

```bash
# Local
psql -U postgres -d breathe_esg

# Remote (Render)
psql -U breathe_user -d breathe_esg -h dpg-xxxxx.postgres.render.com
```

### 5.3 Database User Permissions

Create limited user (production best practice):

```sql
-- As superuser
CREATE USER breathe_app WITH PASSWORD 'generated-password';
GRANT CONNECT ON DATABASE breathe_esg TO breathe_app;

-- Allow read/write on schema
GRANT USAGE ON SCHEMA public TO breathe_app;
GRANT CREATE ON SCHEMA public TO breathe_app;

-- Allow operations on all tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO breathe_app;
```

---

## Part 6: Security Best Practices

### 6.1 .env File Safety

```bash
# Create .env (never commit)
echo ".env" >> .gitignore
cp .env.example .env
# Edit .env with credentials
```

### 6.2 Secure SECRET_KEY

```bash
# ❌ DON'T use default
SECRET_KEY=django-insecure-abc123

# ✅ DO generate random
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6.3 HTTPS Only (Production)

In `settings.py`:
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

### 6.4 Rate Limiting

Install:
```bash
pip install djangorestframework-throttling
```

Configure:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### 6.5 CORS Configuration

```python
# ❌ DON'T allow all
CORS_ALLOW_ALL_ORIGINS = True

# ✅ DO whitelist specific domains
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

### 6.6 SQL Injection Prevention

Django ORM prevents SQL injection automatically:

```python
# ✅ SAFE - uses parameterized queries
records = EmissionRecord.objects.filter(scope=user_input)

# ❌ UNSAFE - never do this
records = EmissionRecord.objects.raw(f"SELECT * FROM records WHERE scope = {user_input}")
```

### 6.7 CSRF Protection

Already enabled in Django. In React forms:
```javascript
// Include CSRF token in POST requests
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/api/records/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrftoken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
```

---

## Part 7: Credential Rotation

### 7.1 Rotate SECRET_KEY

1. Generate new key
2. Update in production environment
3. Existing sessions invalidated (users re-login)
4. No migration needed

### 7.2 Rotate Database Password

```sql
-- As superuser
ALTER USER breathe_user WITH PASSWORD 'new-password';
```

Then update `.env` and redeploy

### 7.3 Rotate API Tokens

```bash
python manage.py shell
```

```python
from rest_framework.authtoken.models import Token

# Delete all tokens (forces re-authentication)
Token.objects.all().delete()

# Or delete specific user
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
Token.objects.filter(user=user).delete()
```

---

## Part 8: Credential Sharing (Safe Way)

### 8.1 Share with Team Members

```bash
# Create temporary credentials file (not the main .env)
# Send via secure channel (1Password, LastPass, etc.)

# DO NOT:
# - Email plain text passwords
# - Commit .env to GitHub
# - Share in Slack/Discord
```

### 8.2 Revoke Access

```bash
# Render Dashboard
Settings → Collaborators → Remove user

# GitHub
Repository Settings → Collaborators → Remove user

# API Token
python manage.py shell
Token.objects.all().delete()
```

### 8.3 Audit Log

Check who accessed what:

```bash
# Django admin logs
http://localhost:8000/admin/admin/logentry/

# Render deployment logs
Render Dashboard → Services → Logs

# GitHub action logs
GitHub → Actions → Workflow runs
```

---

## Part 9: Emergency Procedures

### 9.1 Compromised SECRET_KEY

1. Generate new SECRET_KEY
2. Update in production immediately
3. All user sessions invalidated
4. Users must re-login

### 9.2 Compromised Database Password

1. Change password in PostgreSQL
2. Update environment variables
3. Restart backend service
4. Monitor for unauthorized access

### 9.3 Compromised API Token

```bash
python manage.py shell
```

```python
from rest_framework.authtoken.models import Token
Token.objects.all().delete()  # Invalidate all tokens
# Issue new tokens to authorized users
```

### 9.4 GitHub Repository Compromised

1. Rotate all secrets
2. Remove compromised deploy keys
3. Review commit history for leaked credentials
4. Create new GitHub personal access token

---

## Part 10: Credentials Checklist

### Before Deployment

- [ ] SECRET_KEY generated and changed from default
- [ ] DEBUG = False in production
- [ ] Database password is strong (>16 characters)
- [ ] No credentials in code or comments
- [ ] `.env` file in `.gitignore`
- [ ] `.env.example` created without sensitive values
- [ ] ALLOWED_HOSTS configured for your domain
- [ ] CORS_ALLOWED_ORIGINS restricted
- [ ] HTTPS enabled in production

### After Deployment

- [ ] Superuser created and password changed
- [ ] API tokens rotated if needed
- [ ] Third-party API keys validated
- [ ] Database backups tested
- [ ] Monitoring alerts configured
- [ ] Audit logs reviewed

---

## Part 11: Accessing Credentials in Different Environments

### Local Development
```bash
# Read from .env
cat backend/.env | grep SECRET_KEY
```

### Render Production
```
Dashboard → Services → Your Backend → Environment
(all variables visible to project members)
```

### GitHub Secrets (for CI/CD)
```
GitHub → Settings → Secrets and variables → Actions
```

### Docker Secrets
```bash
docker run --secret db_password myimage
```

---

## Part 12: Reference: Complete Environment Variables

```bash
# ============================================================
# COMPLETE ENVIRONMENT VARIABLE REFERENCE
# ============================================================

# Django Configuration
DEBUG=False
SECRET_KEY=<generated-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FRONTEND_URL=https://your-frontend.vercel.app

# Database Configuration
DB_ENGINE=django.db.backends.postgresql  # or sqlite3
DB_NAME=breathe_esg
DB_USER=breathe_user
DB_PASSWORD=<generated-password>
DB_HOST=localhost  # or RDS endpoint
DB_PORT=5432

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# CORS & CSRF
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1

# Celery (Optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=<optional-error-tracking>

# Third-Party APIs (Optional)
SENDGRID_API_KEY=<key>
GOOGLE_CLIENT_ID=<id>
GITHUB_CLIENT_SECRET=<secret>
```

---

## Summary

| Item | Local Dev | Production |
|------|-----------|-----------|
| SECRET_KEY | dev-key | Generated random |
| Database | SQLite | PostgreSQL |
| DEBUG | True | False |
| HTTPS | ❌ | ✅ |
| Credentials | .env | Environment vars |
| API Token | Optional | Required |
| Logs | Console | File/Service |
| Backups | Manual | Automated |

---

## Quick Reference Commands

```bash
# Generate credentials
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Create superuser
python manage.py createsuperuser

# Create API token
python manage.py shell
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
token, created = Token.objects.get_or_create(user=user)
print(token.key)

# Test database connection
python manage.py shell
from django.db import connection
cursor = connection.cursor()
print("Database connected successfully")

# Change password
python manage.py changepassword admin
```

---

## Support

For security issues:
1. **Do not** post in public issues
2. Email security@example.com
3. Include reproduction steps
4. Request for responsible disclosure timeline

For credential issues:
1. Check credentials guide above
2. Verify `.env` file syntax
3. Check environment variable names exactly
4. Test locally before deploying

---

**Remember**: Credentials are the keys to your system. Handle with care!
