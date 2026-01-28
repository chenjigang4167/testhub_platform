# Copilot / AI Agent Instructions for TestHub

Brief, actionable guidance to help an AI coding agent become productive quickly in this repo.

## Quick overview
- Stack: Django 4.2 (backend) + Vue 3 + Vite (frontend). See [README.md](README.md).
- Repo layout: backend config in [backend/](backend/), Django apps under [apps/](apps/), frontend in [frontend/](frontend/).

## How to run (examples)
- Backend (dev):
  - Create venv, install: `pip install -r requirements.txt`
  - Run migrations and dev server:
    - `python manage.py makemigrations` then `python manage.py migrate`
    - `python manage.py runserver`
  - Useful management commands (implemented in `manage.py` / apps):
    - `python manage.py init_locator_strategies` (UI locator init)
    - `python manage.py download_webdrivers` (download browser drivers)
    - `python manage.py run_scheduled_tasks`

- Frontend:
  - `cd frontend && npm install && npm run dev` (dev server uses Vite)

## Key configuration and conventions
- Primary Django settings: [backend/settings.py](backend/settings.py).
  - Uses `python-decouple` for envs; create `.env` with `DB_*`, `SECRET_KEY`, `REDIS_URL`, etc.
  - Database: MySQL `utf8mb4` (see `DATABASES` in settings).
  - Auth: custom user `AUTH_USER_MODEL = 'users.User'` and JWT via `rest_framework_simplejwt` (see `SIMPLE_JWT`).
  - Celery broker/result backend uses env `REDIS_URL`.

- DRF and API:
  - All APIs are under `/api/`; schema served by drf-spectacular (Swagger: `/api/docs/`).
  - Default renderer is JSON only; do not rely on DRF browsable API in code samples.

- App layout convention:
  - Each feature is a Django app in `apps/` (examples: `apps/api_testing`, `apps/requirement_analysis`, `apps/ui_automation`).
  - Tests live inside each app as `tests.py` or `tests/`.

## AI- and automation-specific hotspots (use these to implement or extend AI features)
- Requirement analysis and AI prompts: `apps/requirement_analysis/` and `tester.md`, `tester_pro.md` (prompt templates).
- UI automation AI: `apps/ui_automation/ai_base.py`, `apps/ui_automation/ai_agent.py`, `apps/ui_automation/ai_models.py` — core Browser-use integrations live here.
- API testing and Allure integration: `apps/api_testing/` and `allure/` directory for report assets.

## Project-specific patterns and gotchas
- AppConfig usage: `apps.ui_automation.apps.UiAutomationConfig` is registered directly in `INSTALLED_APPS` — check `apps/<app>/apps.py` for startup hooks.
- Management commands are used for environment bootstrapping (locator strategies, drivers). Prefer invoking them during local dev rather than re-implementing boot logic.
- Token strategy: JWT Access + Refresh with blacklist; many endpoints assume token refresh behavior. See `backend/settings.py` for `SIMPLE_JWT` ordering.
- Frontend expects API under `http://localhost:8000` and CORS configured for Vite (`5173`) in dev mode.

## Common developer workflows (explicit commands)
- Setup dev DB (MySQL): create DB with `utf8mb4` charset, then run migrations.
- Start backend: `python manage.py runserver` (port 8000).
- Start frontend: `cd frontend && npm run dev` (Vite default 5173).
- Run tests: `python manage.py test` (per-app tests), or use `pytest` if configured.

## Where to look for changes and examples
- API views/serializers: examples in `apps/api_testing/views.py` and `apps/*/serializers.py`.
- Scheduled tasks and background jobs: search `run_scheduled_tasks` and `CELERY` settings.
- UI automation examples and element management: `apps/ui_automation/models.py` and `apps/ui_automation/views.py`.

## Safety and context notes for agents
- Do not hardcode secrets or database credentials; use `.env` and `decouple.config` patterns already in `backend/settings.py`.
- Prefer adding small, well-scoped changes to existing apps rather than large cross-cutting refactors without reviewer approval.
- When adding endpoints, follow existing DRF patterns (viewsets/serializers/routers) and update `drf-spectacular` schema if necessary.

## Contact points / where humans will review
- Major changes to AI prompts or model configs: inspect `apps/requirement_analysis/` and `apps/ui_automation/ai_models.py` and request review from the repo owner.

---
If anything here looks wrong or you'd like more detail about a specific module, tell me which area (backend, frontend, AI modules, or management commands) and I'll expand that section.
