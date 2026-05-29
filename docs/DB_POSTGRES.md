# PostgreSQL (Production)

This app is designed to work with PostgreSQL.

## What “DB Path / Credentials” means here

PostgreSQL itself does not use a “database path” (file path like SQLite). You configure it using:
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

These are required environment variables in `backend/config/settings.py`.

## Required Features
This project uses PostgreSQL features implicitly:
- JSONField (`source_data`, `error_log`, `old_values`, `new_values`)
- UUID PKs (generated in Django)
- Indexes for analyst dashboard filters

## Triggers and sequences
**Not required.**
- Primary keys are UUIDs (`models.UUIDField(default=uuid.uuid4)`)
- Django does not need DB sequences/triggers for UUID primary keys.

## Credentials you must provide
Use your hosting provider’s Postgres credentials.

Required env vars (example):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<your_db_name>
DB_USER=<your_db_user>
DB_PASSWORD=<your_db_password>
DB_HOST=<your_db_host>
DB_PORT=5432
```

## Local + Docker Compose
`docker-compose.yml` already provisions Postgres using:
- DB name: `breathe_esg`
- User: `postgres`
- Password: `postgres`

You can override via environment variables when needed.

