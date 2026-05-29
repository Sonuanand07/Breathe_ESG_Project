# GitHub Push & Submission Guide

Step-by-step guide for pushing Breathe ESG project to GitHub and preparing for submission.

---

## Part 1: GitHub Repository Setup

### 1.1 Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `Breathe_ESG_Project`
   - **Description**: "Enterprise emissions data ingestion and review platform"
   - **Visibility**: **Public** (required for Render free tier)
   - **Initialize with**: Do NOT initialize (we have local code)
3. Click **Create repository**

### 1.2 Get Repository URL

After creation, you'll see:
```
https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git
```

Copy this URL (replace YOUR_USERNAME with your actual username)

---

## Part 2: Prepare Local Repository

### 2.1 Navigate to Project

```bash
cd /path/to/Breathe_ESG_Project
```

### 2.2 Initialize Git (if not done)

```bash
# Initialize repository
git init

# Check status
git status
```

### 2.3 Create .gitignore

Ensure `.gitignore` exists with:

```bash
cat > .gitignore << 'EOF'
# Python
*.py[cod]
__pycache__/
*.egg-info/
*.egg
dist/
build/
.Python
venv/
env/
ENV/
bin/
lib/
Scripts/

# Django
*.sqlite3
db.sqlite3
/staticfiles/
/media/
*.log
*.pot

# Environment variables (NEVER commit)
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Node
node_modules/
npm-debug.log
yarn-error.log
.next/
out/
build/

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Docker
.docker-compose.override.yml
EOF
```

### 2.4 Configure Git User (if first time)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify
git config --list | grep user
```

---

## Part 3: Stage and Commit Code

### 3.1 Add All Files

```bash
# Stage all files
git add .

# Check what will be committed
git status
```

Expected output:
```
On branch main
No commits yet
Changes to be committed:
  new file:   README.md
  new file:   QUICKSTART.md
  new file:   DATABASE_SETUP.md
  new file:   DEPLOY.md
  new file:   TESTING.md
  new file:   CREDENTIALS.md
  new file:   backend/
  new file:   frontend/
  new file:   docs/
  ...
```

### 3.2 Create Initial Commit

```bash
git commit -m "Initial commit: Breathe ESG data ingestion platform

- Django REST API with PostgreSQL/SQLite support
- React dashboard for analyst review workflow
- Multi-tenant architecture with audit trails
- Support for SAP, Utility, and Travel data ingestion
- Complete documentation and deployment guides"
```

### 3.3 Verify Commit

```bash
git log --oneline
# Should show: (HEAD -> main) Initial commit: Breathe ESG data ingestion platform
```

---

## Part 4: Connect to GitHub

### 4.1 Add Remote

```bash
# Replace YOUR_USERNAME with actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git

# Verify
git remote -v
```

Expected output:
```
origin  https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git (fetch)
origin  https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git (push)
```

### 4.2 Set Main Branch (if needed)

```bash
# Rename branch to main (if using old default)
git branch -M main

# Verify
git branch
```

### 4.3 Push to GitHub

```bash
# First push (set upstream)
git push -u origin main

# You may be prompted for credentials:
# - GitHub username
# - GitHub Personal Access Token (PAT) instead of password
```

### 4.4 Generate GitHub Personal Access Token (if needed)

1. Go to https://github.com/settings/tokens/new
2. Configure:
   - **Token name**: `Breathe ESG Push`
   - **Expiration**: 90 days
   - **Scopes**: Select `repo` (full control)
3. Click **Generate token**
4. Copy token and save securely
5. Use as password when pushing

---

## Part 5: Verify GitHub Push

### 5.1 Check Repository

1. Go to https://github.com/YOUR_USERNAME/Breathe_ESG_Project
2. Verify you see:
   - [ ] All files and folders
   - [ ] README.md displayed
   - [ ] Commit history
   - [ ] Main branch selected

### 5.2 Check Files on GitHub

```bash
# Verify files exist (via web browser)
# - backend/
#   - config/settings.py
#   - config/urls.py
#   - apps/core/models.py
#   - apps/core/views.py
#   - apps/ingestion/parsers.py
#   - manage.py
#   - requirements.txt
# - frontend/
#   - src/App.js
#   - src/components/
#   - package.json
# - docs/
#   - MODEL.md
#   - DECISIONS.md
#   - TRADEOFFS.md
#   - SOURCES.md
# - DATABASE_SETUP.md
# - DEPLOY.md
# - TESTING.md
# - CREDENTIALS.md
# - README.md
# - QUICKSTART.md
# - .gitignore
# - docker-compose.yml
```

### 5.3 Verify .env Not Committed

```bash
# Should NOT appear in GitHub
# Check: https://github.com/YOUR_USERNAME/Breathe_ESG_Project/find/main
# Search for ".env" - should return nothing
```

---

## Part 6: Share Access with Evaluators

### 6.1 Grant Repository Access

The assignment requires sharing with:
- saurav@breatheesg.com
- rahul@breatheesg.com
- shivang@breatheesg.com

**Option A: Public Repository** (Recommended for deployment)
- No action needed
- Anyone can view and clone

**Option B: Private Repository with Access Grants**
1. Go to https://github.com/YOUR_USERNAME/Breathe_ESG_Project/settings/access
2. Click "Invite collaborators"
3. Enter each email:
   - saurav@breatheesg.com
   - rahul@breatheesg.com
   - shivang@breatheesg.com
4. Set role to "Maintain" or "Read"
5. Click "Send invitation"

---

## Part 7: Deploy to Render & Vercel

### 7.1 Deploy Backend to Render

Follow [DEPLOY.md - Part 2: Deploy Backend to Render](DEPLOY.md)

### 7.2 Deploy Frontend to Vercel

Follow [DEPLOY.md - Part 3: Deploy Frontend to Vercel](DEPLOY.md)

### 7.3 Get Live URLs

After deployment:
- **Backend URL**: https://breathe-esg-backend.onrender.com
- **Frontend URL**: https://breathe-esg-frontend.vercel.app

---

## Part 8: Prepare Submission Email

### 8.1 Email Template

```
Subject: Breathe ESG Tech Assignment Submission

To: [assignment email]

Dear Breathe ESG Team,

Please find my tech assignment submission below:

GitHub Repository (Public):
https://github.com/YOUR_USERNAME/Breathe_ESG_Project

Live Application:
- Frontend (React Dashboard): https://breathe-esg-frontend.vercel.app
- Backend API: https://breathe-esg-backend.onrender.com/api
- API Documentation: https://breathe-esg-backend.onrender.com/api/docs

Test Credentials:
- Email: admin@example.com
- Password: [your-superuser-password]

Quick Start:
1. Visit frontend URL above
2. Login with credentials above
3. Upload test CSV files (see SAMPLE_DATA.md)
4. View dashboard and approve/reject records

Key Documentation:
- MODEL.md: Data model design and rationale (1000+ lines)
- DECISIONS.md: Design decisions and alternatives (1500+ lines)
- SOURCES.md: Real-world data format research (1200+ lines)
- TRADEOFFS.md: Deliberately excluded features (400+ lines)
- DATABASE_SETUP.md: Database configuration guide
- DEPLOY.md: Deployment and scaling guide
- TESTING.md: Complete testing procedures

Local Setup (Optional):
```bash
git clone https://github.com/YOUR_USERNAME/Breathe_ESG_Project.git
cd Breathe_ESG_Project
docker-compose up -d
docker-compose exec backend python manage.py createsuperuser
# Then access at http://localhost:3000
```

Total Documentation: ~6,000 lines explaining every decision

Best regards,
[Your Name]
```

### 8.2 Prepare Test Data

Create test files for evaluators:

**test_sap.csv**:
```csv
EBELN,EBELP,WERKS,MATNR,MAKTX,BSTME,MENGE,BUDAT,LIFNR,NAME1
4600012345,00010,1000,MAT-001,DIESEL FUEL,L,1500,20240115,200005,ABC Oil
4600012346,00020,1000,MAT-002,PETROL,L,500,20240116,200005,ABC Oil
```

**test_utility.csv**:
```csv
meter_id,facility_name,utility_provider,billing_period_start,billing_period_end,consumption_kwh,tariff_name
MTR-001,SF HQ,PG&E,2024-01-12,2024-02-16,2595,A-10
```

**test_travel.csv**:
```csv
trip_id,travel_mode,departure_airport,arrival_airport,seat_class,distance_km,number_of_nights,expense_date
TRIP-001,flight,SFO,JFK,economy,4160,,2024-01-15
TRIP-002,hotel,,,,,3,2024-01-16
```

---

## Part 9: Verify Everything Works

### 9.1 Test Live Application

1. Open frontend URL
2. Login with test credentials
3. Upload test CSV
4. Verify data appears
5. Approve/reject records
6. Check audit trail

### 9.2 Test API Documentation

```bash
# Visit API docs
curl https://breathe-esg-backend.onrender.com/api/docs

# Test endpoints
curl https://breathe-esg-backend.onrender.com/api/clients/
curl https://breathe-esg-backend.onrender.com/api/records/
```

### 9.3 Test Database

```bash
# Connect to live database (if needed)
psql -U breathe_user -h breathe-esg-db.xxx.postgres.render.com -d breathe_esg
```

### 9.4 Verify Documentation

Check all files are present and readable:
- [ ] README.md - accessible at repository root
- [ ] QUICKSTART.md - quick start guide
- [ ] DATABASE_SETUP.md - database configuration
- [ ] DEPLOY.md - deployment guide
- [ ] TESTING.md - testing procedures
- [ ] CREDENTIALS.md - credentials guide
- [ ] docs/MODEL.md - data model documentation
- [ ] docs/DECISIONS.md - design decisions
- [ ] docs/TRADEOFFS.md - excluded features
- [ ] docs/SOURCES.md - source research

---

## Part 10: Post-Submission Checklist

### Before Sending Submission

- [ ] Repository pushed to GitHub
- [ ] All files committed (no pending changes)
- [ ] .env file NOT committed
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Live URLs are accessible
- [ ] Test data can be uploaded
- [ ] Approval workflow works
- [ ] Documentation complete
- [ ] Credentials shared with evaluators

### Submission Information

Collect and prepare:

```
GitHub Repository: https://github.com/YOUR_USERNAME/Breathe_ESG_Project
Frontend URL: https://breathe-esg-frontend.vercel.app
Backend URL: https://breathe-esg-backend.onrender.com/api
Admin Email: admin@example.com
Admin Password: [your superuser password]
```

### Deployment Credentials

Keep available but SECURE:

```
Render:
- Dashboard: https://dashboard.render.com
- Service: breathe-esg-backend

Vercel:
- Dashboard: https://vercel.com
- Project: breathe-esg-frontend

GitHub:
- Repository: https://github.com/YOUR_USERNAME/Breathe_ESG_Project
- Personal Access Token: [secure location]
```

---

## Part 11: Continuous Updates

### 11.1 Make Changes After Submission

```bash
# Make changes locally
vim backend/apps/core/models.py

# Commit changes
git add .
git commit -m "Update model documentation"

# Push to GitHub (auto-deploys to Render/Vercel)
git push origin main
```

### 11.2 Monitor Deployments

**Render**: https://dashboard.render.com/services
**Vercel**: https://vercel.com/dashboard

Both auto-redeploy when you push to main.

### 11.3 View Logs

**Render Logs**:
```
Dashboard → Services → breathe-esg-backend → Logs
```

**Vercel Logs**:
```
Dashboard → Projects → breathe-esg-frontend → Deployments
```

---

## Part 12: Troubleshooting

### Issue: "Please make sure you have the correct access rights"

**Solution**:
```bash
# Use personal access token instead of password
git remote set-url origin https://<token>@github.com/YOUR_USERNAME/Breathe_ESG_Project.git
git push origin main
```

### Issue: Files missing on GitHub

**Solution**:
```bash
# Verify all files staged
git status

# Add forgotten files
git add forgotten-file.txt

# Commit and push
git commit -m "Add forgotten files"
git push origin main
```

### Issue: Deployment fails after push

**Solution**:
1. Check Render/Vercel logs
2. Fix issue locally
3. Commit fix
4. Push (auto-redeploy)

### Issue: .env file accidentally committed

**Solution**:
```bash
# Remove from git history
git rm --cached backend/.env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Remove .env from version control"
git push origin main

# Regenerate secrets (they may be compromised)
```

---

## Submission Checklist

### Final Verification

- [ ] **Repository**: Pushed to GitHub and accessible
- [ ] **Backend**: Live on Render at https://breathe-esg-backend.onrender.com
- [ ] **Frontend**: Live on Vercel at https://breathe-esg-frontend.vercel.app
- [ ] **Database**: Connected and working on Render PostgreSQL
- [ ] **Credentials**: Test user created and working
- [ ] **Documentation**: All 6 files complete (>6000 lines)
- [ ] **Data Model**: Comprehensive MODEL.md (1000+ lines)
- [ ] **Decisions**: DECISIONS.md with full rationale (1500+ lines)
- [ ] **Research**: SOURCES.md with real-world formats (1200+ lines)
- [ ] **Tradeoffs**: TRADEOFFS.md with 3 excluded features (400+ lines)
- [ ] **Deployment**: DEPLOY.md with Render & Vercel guides
- [ ] **Database**: DATABASE_SETUP.md with SQLite & PostgreSQL
- [ ] **Testing**: TESTING.md with comprehensive test cases
- [ ] **Sample Data**: Test CSV files provided
- [ ] **Credentials**: Guide for managing secrets

---

## Summary

| Step | Command | Status |
|------|---------|--------|
| 1 | Create GitHub repo | ✓ |
| 2 | Initialize local git | ✓ |
| 3 | Commit code | ✓ |
| 4 | Push to GitHub | ✓ |
| 5 | Deploy backend to Render | ✓ |
| 6 | Deploy frontend to Vercel | ✓ |
| 7 | Share access with evaluators | ✓ |
| 8 | Send submission email | ✓ |
| 9 | Provide test credentials | ✓ |
| 10 | Monitor deployments | ✓ |

---

## Quick Reference

```bash
# View current status
git status
git log --oneline
git remote -v

# Add and commit changes
git add .
git commit -m "Your commit message"

# Push changes
git push origin main

# View GitHub
open https://github.com/YOUR_USERNAME/Breathe_ESG_Project

# Monitor deployment
open https://dashboard.render.com
open https://vercel.com/dashboard
```

---

**Your Breathe ESG project is now complete, deployed, and ready for evaluation!**

---

## Additional Resources

- [GitHub Getting Started](https://docs.github.com/en/get-started)
- [Render Deployment Documentation](https://render.com/docs)
- [Vercel Deployment Documentation](https://vercel.com/docs)
- [Django Deployment Best Practices](https://docs.djangoproject.com/en/4.2/howto/deployment/)
