# SQLite Database Path (requested)

Use SQLite for local testing by pointing `DB_NAME` to the SQLite file path.

## Path
Recommended:
- `backend/db.sqlite3`

Alternative (also works):
- `db.sqlite3` at the repo root

## Env example

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=backend/db.sqlite3
```

## Note
PostgreSQL does **not** use a path; it uses host/user/password/database name.

