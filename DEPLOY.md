# Deployment Guide - Render & Vercel

Complete step-by-step guide to deploy Breathe ESG to Render (backend + database) and Vercel (frontend).

---

## Deployment Architecture

```
GitHub Repository
    ↓
    ├─→ Render (Backend + PostgreSQL)
    │   └─ https://your-app.onrender.com/api
    │
    └─→ Vercel (Frontend React)
        └─ https://your-app-frontend.vercel.app
```

---

## Part 1: Prepare GitHub Repository

### 1.1 Initialize Git (if not already done)

```bash
cd /path/to/Breathe_ESG_Project
git init
git add .
git commit -m "Initial commit: Breathe ESG platform"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `Breathe_ESG_Project`
3. Description: "Enterprise emissions data ingestion and review platform"
4. Visibility: **Public** (required for free deployments)
5. Click "Create repository"

### 1.3 Connect Local to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git
git branch -M main
git push -u origin main
```

Verify:
```bash
git remote -v
# Output should show:
# origin  https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git (fetch)
# origin  https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git (push)
```

---

## Part 2: Deploy Backend to Render

### 2.1 Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (easier for deployment)
3. Authorize GitHub access
4. Link your GitHub account

### 2.2 Create PostgreSQL Database on Render

1. Dashboard → **New +** button
2. Select **PostgreSQL**
3. Configure:
   - **Name**: `breathe-esg-db`
   - **Database**: `breathe_esg`
   - **User**: `breathe_user`
   - **Password**: Generate strong password (save this!)
   - **Region**: Select closest to you
   - **Version**: 15 (or latest)
   - **Plan**: Free (for testing)
4. Click **Create Database**
5. Wait 3-5 minutes for database to initialize
6. Copy the **Internal Database URL** (looks like `postgresql://...`)

### 2.3 Create Web Service (Backend) on Render

1. Dashboard → **New +** button
2. Select **Web Service**
3. Configure:

#### Repository Connection
   - Select repository: `Breathe_ESG_Project`
   - Branch: `main`
   - Auto-deploy: ✅ On (redeploy on every push)

#### Build & Deploy
   - **Name**: `breathe-esg-backend`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt && cd backend && python manage.py migrate
     ```
   - **Start Command**:
     ```bash
     cd backend && gunicorn config.wsgi:application
     ```

#### Environment Variables
Click **Environment** and add:
   ```
   DEBUG=False
   SECRET_KEY=<generate-secure-key>
   ALLOWED_HOSTS=breathe-esg-backend.onrender.com
   FRONTEND_URL=https://<your-vercel-app>.vercel.app
   
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=breathe_esg
   DB_USER=breathe_user
   DB_PASSWORD=<your-database-password>
   DB_HOST=<internal-database-url-host>
   DB_PORT=5432
   ```

4. Click **Create Web Service**
5. Wait for deployment (5-10 minutes)
6. Copy the **Live URL**: `https://breathe-esg-backend.onrender.com`

### 2.4 Render Backend Troubleshooting

#### Check Deployment Status
```
Render Dashboard → Your Service → Logs
```

#### Common Issues

**Issue**: "ModuleNotFoundError: No module named 'django'"
**Solution**: 
- Check `backend/requirements.txt` exists
- Verify Build Command uses correct path

**Issue**: "ImportError: Cannot import name 'SPECTACULAR_SETTINGS'"
**Solution**:
```bash
pip install drf-spectacular
# Add to requirements.txt
```

**Issue**: "Django.core.exceptions.ImproperlyConfigured"
**Solution**:
- Verify SECRET_KEY is set in environment
- Check DB_HOST, DB_USER, DB_PASSWORD

#### Verify Deployment

```bash
# Test API is live
curl https://breathe-esg-backend.onrender.com/api/

# Test database connection
curl https://breathe-esg-backend.onrender.com/api/docs
```

---

## Part 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account

1. Go to https://vercel.com
2. Sign up with GitHub
3. Authorize GitHub access
4. Link your GitHub account

### 3.2 Deploy Frontend

1. Dashboard → **Add New...** → **Project**
2. Select your repository: `Breathe_ESG_Project`
3. Configure:

#### Project Settings
   - **Project Name**: `    `
   - **Framework Preset**: Select **React**
   - **Root Directory**: `./frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

#### Environment Variables
Click **Environment Variables** and add:
   ```
   REACT_APP_API_URL=https://breathe-esg-backend.onrender.com/api
   ```

4. Click **Deploy**
5. Wait for deployment (3-5 minutes)
6. Copy the **Vercel URL**: `https://breathe-esg-frontend.vercel.app`

### 3.3 Update Backend CORS (Back to Render)

1. Go to Render Dashboard
2. Select your backend service
3. Click **Settings** → **Environment**
4. Update:
   ```
   FRONTEND_URL=https://breathe-esg-frontend.vercel.app
   CORS_ALLOWED_ORIGINS=https://breathe-esg-frontend.vercel.app
   ```
5. Click **Deploy** (automatic redeploy)

### 3.4 Vercel Frontend Troubleshooting

#### Check Deployment
```
Vercel Dashboard → Your Project → Deployments
```

#### Common Issues

**Issue**: "API calls failing with CORS error"
**Solution**:
- Verify REACT_APP_API_URL is correct
- Check backend CORS_ALLOWED_ORIGINS includes Vercel URL
- Wait 2 minutes after updating for cache to clear

**Issue**: "Cannot find module"
**Solution**:
- Ensure `frontend/package.json` has all dependencies
- Run locally: `cd frontend && npm install && npm start`

**Issue**: Blank/white page
**Solution**:
- Check browser console for errors (F12)
- Verify API URL is reachable
- Check Vercel deployment logs

#### Test Frontend

```bash
# Open in browser
https://breathe-esg-frontend.vercel.app

# Login with credentials created during backend setup
# Test API connection: Open DevTools → Network tab → check API calls
```

---

## Part 4: Configure Production Environment

### 4.1 Generate Secure SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Example output:
```
'@v$%b3j1k2!v@_p@!w_8$!#=i@k@=n)%wz=@p^h)x_0z$oa0b'
```

Copy this and add to Render environment variables as `SECRET_KEY`

### 4.2 Update Allowed Hosts

On Render backend service → Environment:
```
ALLOWED_HOSTS=breathe-esg-backend.onrender.com,your-custom-domain.com
```

### 4.3 Create Superuser on Production

```bash
# SSH into Render service (if available) OR
# Run via Render shell

# Via Render Dashboard:
# Services → Your Backend → Shell → Run:
python manage.py createsuperuser

# Follow prompts to create admin account
```

Then access admin at: `https://breathe-esg-backend.onrender.com/admin`

### 4.4 Load Initial Data (Optional)

```bash
# Create test client and data sources via Django admin or API

# Via API:
curl -X POST https://breathe-esg-backend.onrender.com/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Company","legal_entity_id":"TEST-001"}'
```

---

## Part 5: Continuous Deployment Setup

### 5.1 Auto-Deploy on Git Push

Both Render and Vercel automatically deploy when you push to main:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Automatically triggers:
# - Backend redeployment on Render
# - Frontend redeployment on Vercel
```

### 5.2 Preview Deployments (Vercel)

Create a feature branch to test before merging to main:

```bash
git checkout -b feature/new-feature
# Make changes
git push origin feature/new-feature

# Vercel automatically creates preview URL
# Check Pull Requests for preview link
```

### 5.3 Deployment Environment

Create `.env.production` (don't commit):
```bash
DEBUG=False
SECRET_KEY=your-production-key
ALLOWED_HOSTS=your-domain.com
FRONTEND_URL=https://your-frontend.vercel.app
```

---

## Part 6: Monitoring & Logs

### 6.1 Backend Logs (Render)

```
Dashboard → Services → breathe-esg-backend → Logs
```

View real-time logs of API requests and errors

### 6.2 Frontend Logs (Vercel)

```
Dashboard → Projects → breathe-esg-frontend → Deployments → Logs
```

View build logs and runtime errors

### 6.3 Database Monitoring (Render)

```
Dashboard → Databases → breathe-esg-db → Logs
```

Monitor database performance and connection issues

### 6.4 Common Production Issues

**Issue**: "502 Bad Gateway"
**Solution**:
- Check backend logs on Render
- Verify database connection
- Check environment variables

**Issue**: "CSRF verification failed"
**Solution**:
- Ensure CORS_ALLOWED_ORIGINS is set correctly
- Add CSRF_TRUSTED_ORIGINS to backend

**Issue**: "Static files not loading"
**Solution**:
```bash
# On Render backend:
python manage.py collectstatic --noinput
```

---

## Part 7: Custom Domain (Optional)

### 7.1 Add Custom Domain to Render

1. Render Dashboard → Services → Your Backend
2. Settings → Custom Domains
3. Enter your domain (e.g., `api.example.com`)
4. Add DNS CNAME record to your domain provider

### 7.2 Add Custom Domain to Vercel

1. Vercel Dashboard → Project Settings
2. Domains → Add Custom Domain
3. Follow DNS instructions for your provider

---

## Part 8: Backup & Recovery

### 8.1 Database Backups (Render)

Render PostgreSQL automatically creates daily backups. Access via:
```
Dashboard → Databases → breathe-esg-db → Backups
```

### 8.2 Manual Backup

```bash
# Download database backup
pg_dump -U breathe_user -h <db-host> breathe_esg > backup.sql
```

### 8.3 Recovery

```bash
# Restore from backup
psql -U breathe_user -h <db-host> breathe_esg < backup.sql
```

---

## Part 9: Scaling & Performance

### 9.1 Render Scaling

1. Services → Your Backend → Settings
2. Plan: Upgrade from Free to Standard
3. Auto-scaling: Configure minimum/maximum instances

### 9.2 Database Scaling

1. Databases → Your Database → Settings
2. Plan: Upgrade from Free to Starter+
3. Configure automated backups

### 9.3 Frontend Performance (Vercel)

Vercel automatically optimizes:
- [ ] Static file caching
- [ ] Image optimization
- [ ] Code splitting
- [ ] Edge caching

---

## Part 10: Deployment Checklist

### Before Deploying

- [ ] All code committed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `frontend/package.json` includes all dependencies
- [ ] `DATABASE_SETUP.md` reviewed
- [ ] Test locally with `docker-compose up`

### Render Deployment

- [ ] PostgreSQL database created
- [ ] Secret key generated and added
- [ ] Build command correct: `pip install -r backend/requirements.txt && cd backend && python manage.py migrate`
- [ ] Start command correct: `cd backend && gunicorn config.wsgi:application`
- [ ] All environment variables set
- [ ] Migrations ran successfully (check logs)
- [ ] Superuser created
- [ ] API accessible at `/api/docs`

### Vercel Deployment

- [ ] Repository connected
- [ ] Root directory set to `./frontend`
- [ ] REACT_APP_API_URL set correctly
- [ ] Frontend builds successfully
- [ ] Redirects configured (if using React Router)

### Post-Deployment

- [ ] Test API endpoints: `curl https://backend-url/api/docs`
- [ ] Test frontend: Open https://frontend-url in browser
- [ ] Create test data in admin panel
- [ ] Test file upload functionality
- [ ] Test approval workflow
- [ ] Check logs for errors
- [ ] Monitor performance for 24 hours

---

## Part 11: Troubleshooting Deployment

### General Debugging

```bash
# Check if services are responding
curl -v https://your-backend.onrender.com/api/
curl -v https://your-frontend.vercel.app

# Check CORS headers
curl -i -X OPTIONS \
  -H "Origin: https://your-frontend.vercel.app" \
  https://your-backend.onrender.com/api/
```

### Database Connection Issues

1. Verify internal database URL is correct
2. Check credentials in environment variables
3. Test connection: `psql -d postgresql://... `
4. Check Render database status (ensure it's running)

### Build Failures

1. Check build logs in dashboard
2. Verify build command is correct
3. Ensure all dependencies in `requirements.txt`
4. Test locally: `pip install -r requirements.txt`

### Performance Issues

1. Monitor Render service metrics
2. Check database query performance
3. View Vercel analytics
4. Consider upgrading from Free tier

---

## Part 12: Live Deployment Summary

After following all steps, you'll have:

```
Frontend (Vercel)
└─ https://breathe-esg-frontend.vercel.app
   ├─ Dashboard
   ├─ Login
   └─ File Upload

Backend (Render)
└─ https://breathe-esg-backend.onrender.com
   ├─ API: /api/
   ├─ Admin: /admin/
   ├─ Docs: /api/docs/
   └─ Database: PostgreSQL on Render

GitHub
└─ https://github.com/YOUR_USERNAME/Breathe_ESG_Project
   └─ Auto-deploys on every push to main
```

---

## Next Steps

1. **Deploy Backend**: Follow Part 2
2. **Deploy Frontend**: Follow Part 3
3. **Test Integration**: Verify both services communicate
4. **Share URLs**: Send deployment links to evaluators
5. **Monitor**: Watch logs for errors in first 24 hours

---

## Reference URLs

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [PostgreSQL on Render](https://render.com/docs/postgresql)

---

## Support

**Issue**: Deployment fails with error
**Solution**: Check logs first:
- Render: Services → Logs
- Vercel: Deployments → Logs

**Need rollback?**
```bash
git revert HEAD
git push origin main
# Automatic redeploy happens immediately
```

---

**Total Deployment Time**: ~20 minutes
**Difficulty**: Medium (follow step-by-step)
**Cost**: Free (with Render Free tier) or Upgrade as needed
