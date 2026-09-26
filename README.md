# Task Manager API

A FastAPI backend with users, JWT auth, and task CRUD — the skeleton for the
mid-level Python project. This gets you through Phase 1 and 2 of the guide
(foundation + CRUD/auth) with working code. Phase 3 (background jobs with
Celery, rate limiting) and Phase 4 (Docker polish, deeper tests) are yours
to build on top of this.

## What's here

- `app/main.py` — FastAPI app, mounts the routers
- `app/core/` — settings (`config.py`) and auth helpers (`security.py`)
- `app/models/` — SQLAlchemy models (`User`, `Task`)
- `app/schemas/` — Pydantic request/response shapes
- `app/api/routes/` — HTTP handlers (thin — they call services, don't contain logic)
- `app/services/` — the actual business logic and authorization rules
- `app/db/session.py` — async engine + session
- `tests/` — pytest suite covering auth and task authorization boundaries

## Running it locally (without Docker)

1. Create and activate a virtualenv:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy the env template and fill it in:
   ```
   cp .env.example .env
   ```
4. Make sure Postgres is running locally and the DB in `DATABASE_URL` exists.
5. Set up Alembic and generate your first migration (not included yet —
   run `alembic init alembic`, point `alembic.ini` / `env.py` at
   `app.db.session.Base` and `settings.database_url`, then:
   ```
   alembic revision --autogenerate -m "create users and tasks tables"
   alembic upgrade head
   ```
6. Run the API:
   ```
   uvicorn app.main:app --reload
   ```
7. Open `http://localhost:8000/docs` for interactive Swagger UI.

## Running it with Docker

```
docker-compose up --build
```

This starts the API, Postgres, and Redis together. You'll still need to run
the Alembic migration once the containers are up (`docker-compose exec api
alembic upgrade head`), or add that as a startup step once you're comfortable
with it.

## Running the tests

```
pytest
```

Tests run against an in-memory SQLite database (see `tests/conftest.py`), so
no external services are needed to run them. Swapping this for a real
throwaway Postgres via `testcontainers` is a good next step once the basics
are solid — SQLite and Postgres don't behave identically for everything
(enum handling, in particular, is looser in SQLite).

## What's intentionally left for you to build

Straight from the project guide — this scaffold stops right where the
"mid-level differentiators" phase begins:

- [ ] Custom exception → global handler wiring for consistent error JSON
- [ ] Celery + Redis background job (e.g. due-date reminders)
- [ ] Rate limiting on `/auth/login`
- [ ] Alembic migrations (structure is ready, migrations aren't generated)
- [ ] Deploying it somewhere real

## Design notes

- **Schemas are separate from models.** `UserOut` never includes
  `hashed_password` — this is deliberate, not an oversight to fix later.
- **Services own authorization.** `_get_owned_task` in `task_service.py` is
  the single place that enforces "you can only touch your own tasks" — every
  route gets this check by going through it, rather than each route
  re-implementing the check (and potentially forgetting it).
- **Routes stay thin.** They parse input, call a service, translate service
  exceptions into HTTP status codes. No business logic lives in `api/routes/`.
