# Deployment Fixes (Render + Vercel) + Auth/Client selection

## 1) Render build failing: `Could not open requirements file: backend/requirements.txt`

### Why it happens
Render runs the build command from your repo root (or sometimes a different working dir). If the build command assumes a different working directory, `backend/requirements.txt` cannot be found.

### Fix (set the Render Web Service Build Command exactly to this)
In **Render → Backend Web Service → Build Command** use:

```bash
cd backend && pip install -r requirements.txt
```

Then in **Render → Backend Web Service → Start Command** use:

```bash
cd backend && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

> This guarantees the working directory is always `backend/` so `requirements.txt` is found.

## 2) Render failing with `ModuleNotFoundError: No module named 'drf_spectacular'`

### Why it happens
The requirements were not installed (because build step failed) OR the wrong requirements file was used.

### Fix
After applying section (1), this should resolve automatically because `drf-spectacular==0.26.5` is already present in:

- `backend/requirements.txt`

## 3) Frontend upload error: “Please select a client from the sidebar first.”

### Why it happens
`frontend/src/components/DataIngestion.jsx` blocks submission if `selectedClient` is null.

`selectedClient` is set in:
- `frontend/src/App.js` only after `api.getClients()` succeeds.

If backend auth is enforced (`IsAuthenticated`) and the frontend login does not authenticate against Django, then `GET /api/clients/` fails and `selectedClient` never gets set.

### Short-term workaround (no auth endpoint implemented)
Seed at least one client using Django admin on the backend, then temporarily relax auth for development OR implement `/api/auth/login/`.

### Recommended (proper fix)
Implement Django auth login endpoint and update `frontend/src/components/Login.jsx` to request a real token.

## 4) Docker sanity check (optional)
If you want to verify quickly before redeploy:

```bash
docker-compose up --build
```

Then:
- verify backend boots
- verify `/api/clients/` responds
- verify frontend sidebar can load clients

---

If you want, I can implement the missing auth endpoint + update the frontend to use it so client selection works in production.

