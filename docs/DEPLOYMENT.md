# Deployment (Render + Vercel + Local)

This project is a **Django REST API (backend)** + **React SPA (frontend)**.

- Backend base URL: `/api`
- Backend API docs: `https://<backend-domain>/api/docs`
- Frontend should call: `REACT_APP_API_URL=https://<backend-domain>/api`

> **Important**: This repository currently uses **DRF authentication with `IsAuthenticated`**, but there is **no backend `/api/auth/login/` endpoint** implemented in the Django code. The included React login page currently uses a local “demo token” and does not authenticate with Django.
>
> The deployment steps below focus on database setup + build/deploy correctness. For a fully working authenticated end-to-end demo, we need to add an auth endpoint (login) and token auth (see `docs/AUTH.md` which will be created in the next step if you request code changes).

---

## A) SQLite local testing (database path)

Even if production uses Postgres, use SQLite for quick local development.

### 1) Create a SQLite DB file

Example path (recommended):
- `backend/db.sqlite3`

### 2) Environment variables (local)

Create `backend/.env` (or export env vars):

```env
DEBUG=True
SECRET_KEY=local-dev-secret
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=backend/db.sqlite3
FRONTEND_URL=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3) Run migrations

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## B) Render (Postgres + Backend + Frontend)

### 1) Create Postgres on Render

1. Go to Render dashboard → **New +** → **PostgreSQL**
2. Create instance (pick free tier if available)
3. Note the connection settings from Render (database URL / host / username / password / db name)

### 2) Deploy Backend to Render

1. Render → **New +** → **Web Service**
2. Name: `breathe-esg-backend`
3. Build command:

```bash
pip install -r requirements.txt && python manage.py migrate
```

(If Render runs your project from repo root, ensure you set the working directory; otherwise use `cd backend` in the command.)

Recommended build/start with explicit directories:

- Build command:

```bash
cd backend && pip install -r requirements.txt
```

- Start command:

```bash
cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

4. Environment variables (set in Render):

```env
DEBUG=False
SECRET_KEY=<generate-a-secret>
ALLOWED_HOSTS=<your-render-service-host>
FRONTEND_URL=<your-frontend-render-or-vercel-url>

# Postgres (use the Render-provided values)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<render-db-name>
DB_USER=<render-db-user>
DB_PASSWORD=<render-db-password>
DB_HOST=<render-db-host>
DB_PORT=5432

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

> If Redis is not deployed on Render, you can temporarily disable Celery usage or set broker/result to a dummy local Redis only for dev.

### 3) Deploy Frontend (Vercel/Render static)

Frontend is a React SPA. Recommended approach:

- Deploy as static site (Render Static Web Apps or Vercel)
- Ensure env var points to backend API:

`REACT_APP_API_URL=https://<backend-host>/api`

Render example build/start:
- Build command: `cd frontend && npm install && npm run build`
- For static serving: you can use `serve -s build`.

---

## C) Vercel (Frontend)

Vercel is best for the React frontend. Deploy frontend and set:

- Framework preset: **Create React App**
- Build command: `cd frontend && npm install && npm run build`
- Output directory: `frontend/build`

Environment variables in Vercel:

```env
REACT_APP_API_URL=https://<backend-host>/api
```

### Backend on Vercel?

Deploying Django on Vercel is possible but usually not the simplest. Recommended is: **Render backend + Vercel frontend**.

---

## D) Render/Railway/Vercel credentials: what you must provide

This repo does not store secrets. You must set these values in your hosting provider:

- `SECRET_KEY`
- Postgres: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `ALLOWED_HOSTS`
- `FRONTEND_URL`
- (Optional) `CELERY_*` if Celery is used

Do not use placeholder credentials. Always use provider-generated credentials.

---

## E) Verify deployment

1. Open backend docs:
   - `https://<backend-host>/api/docs`
2. Open frontend:
   - `https://<frontend-host>`
3. In browser devtools, confirm:
   - CORS is working
   - Frontend is calling `REACT_APP_API_URL`

> End-to-end “login” requires implementing a Django auth endpoint. Current frontend login is demo-only.

