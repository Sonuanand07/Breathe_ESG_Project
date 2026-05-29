# TODO

## Plan execution checklist
- [ ] Inspect current backend routing (done: read backend/config/urls.py)
- [ ] Implement health endpoint at `/` so Render/Open check doesn’t return 404
- [ ] Confirm no other URL conflicts
- [ ] Run backend tests or `python manage.py check` (optional)
- [ ] (If applicable) redeploy/run Gunicorn and verify `/` returns 200

