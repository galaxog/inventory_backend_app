# Sample Inventory Service

FastAPI + Postgres + SQLAlchemy + Alembic service

This project is generated from a Cookiecutter template and includes:

- **FastAPI** app factory (`app/create_app`)
- **Postgres + SQLAlchemy 2.x** engine/session configured in `app/models/__init__.py`
- **Alembic** migrations in `migrations/`
- **Users + JWT auth** modules:
  - `api/users` (registration)
  - `api/authentication` (login + refresh)

---

## Project layout

```
app/
  __init__.py          # create_app factory + router wiring + JWT config
  main.py              # uvicorn entrypoint
  app_config.py        # settings (dev/testing/prod)
  state.py             # process-local initialization (settings + db engine/session)
  models/
    __init__.py        # engine/session + Base + naming conventions (alembic-friendly)
    user.py            # User model
    token.py           # RefreshToken model (stored by JTI)
  api/
    users/
      schemas.py
      view.py
      tests/
        test_users.py
    authentication/
      schemas.py
      view.py
      tests/
        test_authentication.py
migrations/
  env.py               # alembic config (uses app_config)
  versions/
```

---

## Configuration

Copy the example env file:

```bash
cp .env.example .env
```

Key variables:

- `ENVIRONMENT` (`development` | `testing` | `production`)
- `SQLALCHEMY_DATABASE_URI` (Postgres connection string)
- `SQLALCHEMY_DATABASE_URI_TEST` (used when `ENVIRONMENT=testing`)
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`
- `JWT_ACCESS_TOKEN_EXPIRES_HOURS`, `JWT_REFRESH_TOKEN_EXPIRES_HOURS`

---

## Local development

Create a venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run migrations:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Run the API:

```bash
uvicorn app.main:app --reload
```

---

## Authentication flow

### Endpoints

- `POST /api/users/register` — create a user
- `POST /api/authentication/login` — returns `{access_token, refresh_token}`
- `POST /api/authentication/refresh` — rotates refresh token and returns a new pair

### Refresh tokens stored by JTI

Refresh tokens are **not stored in the database as raw tokens**. Instead, the DB stores the **JTI** (unique token id) from the refresh JWT in the `refresh_tokens` table.

On refresh:

1. Client sends the refresh token in the `Authorization: Bearer <refresh>` header
2. Server extracts the token **JTI** and looks it up in `refresh_tokens`
3. If present and not revoked/expired → server **revokes** the old JTI row and issues a new access+refresh pair
4. The new refresh token’s JTI is inserted as a new DB row

This gives you rotation/revocation without storing the raw refresh token.

### Example curl

Register:

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"a@example.com","password":"Password123!"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/authentication/login \
  -H "Content-Type: application/json" \
  -d '{"email":"a@example.com","password":"Password123!"}'
```

Refresh:

```bash
curl -X POST http://localhost:8000/api/authentication/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

---

## Tests

Run tests:

```bash
pytest
```

The included pytest fixtures create the FastAPI app using `create_app("testing")` and create/drop tables for the session.

---

## Docker Compose

Build + run (API + Postgres):

```bash
docker compose up --build
```

The API container runs:

- `alembic upgrade head`
- then starts Uvicorn on `0.0.0.0:8000`

If you prefer to manage migrations manually, edit `docker-compose.yml` and remove the `alembic upgrade head` part from the command.
