# Rubitech Academy

Interactive SQL learning platform: static frontend (in-browser SQLite via sql.js) + FastAPI backend that authenticates students, grades submissions in a sandbox and awards XP.

## Run locally (two terminals)

Backend (http://localhost:8000, docs at /docs):
```
cd backend
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```
Frontend (http://localhost:5173):
```
python serve.py
```
Test the backend: `cd backend && python -m pytest -q`

By default the API uses SQLite (`academy.db`). For PostgreSQL set `DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db` in `backend/.env`.

## Structure
- `index.html` – landing page; `app.html` – login + learning app
- `js/data.js` – public lesson content and dataset (no answers)
- `backend/app/content/lessons.json` – starter curriculum, loaded into the `lessons` table on first run (content is then managed in the DB by admins)
- `backend/app/grader.py` – sandboxed grader (fresh in-memory SQLite per run, ATTACH/PRAGMA blocked, 2 s time limit)
- `backend/app/services/gamification.py` – once-only XP ledger, streaks, badges, leaderboard
- `backend/app/routers/` – `/api/v1` auth and learning endpoints

## API (`/api/v1`)
`POST /auth/register` · `POST /auth/login` · `POST /auth/logout` · `GET /auth/me` · `GET /progress` · `POST /submissions` · `POST /lessons/{id}/hint` · `GET /hints/{id}` · `GET /lessons` · `GET /achievements` · `GET /leaderboard`

Admin (role `admin` only): `GET/POST /admin/lessons` · `PUT /admin/lessons/{id}` · `POST /admin/lessons/{id}/publish` · `POST /admin/lessons/{id}/check` · `GET /admin/students` · `GET /admin/stats`

User management (Admin → Students tab): `POST /admin/users` (add) · `POST /admin/users/{id}/role` · `POST /admin/users/{id}/active` (disable/enable) · `POST /admin/users/{id}/reset-password` · `POST /admin/users/{id}/reset-progress` · `DELETE /admin/users/{id}`. Admins can open any lesson regardless of order, are excluded from the leaderboard, and cannot disable, demote or delete themselves or the last active admin.

## Courses (SQL now, Python and more later)
Content is organised as **Course → Module → Lesson**. Admins create courses and modules in the Admin → Courses tab. Each course has a *runtime* that runs and grades its tasks; only `sql` exists today (`backend/app/runtimes.py`). Python, JavaScript etc. can be drafted but not published until a runtime is added: implement `run` + `grade` in an isolated sandbox (never in the API process) and register it in `RUNTIMES`.

Colours live in the `:root` block of `css/styles.css` (primary #4A1942, secondary #8B3A62, accent #FF8066, background #FFF1ED).

## Python course
`backend/app/content/courses/python/` holds `course.json` and one `levelN.json` per level (8 levels, 113 tasks). They are loaded into the database on first start (a course with no lessons yet). Authoring format: `backend/app/content/courses/AUTHORING.md`. Check content with:
```
python backend/validate_course.py python
```
Python tasks run in a **separate sandboxed process** (`backend/app/pyrunner.py`, `pysandbox_child.py`): 5 s limit, no network or subprocesses, files only inside a temporary folder. Students press **Run** to try code (`POST /run`, no XP) and **Submit** to grade it against hidden tests. This is defence in depth, not a perfect jail: for a public launch run the API's Python runner on a separate low-privilege host or VM.

## Brand
Rubitech Academy logo files are in `assets/logo/` (badge, one-colour badge, horizontal lockup, reverse lockup); `favicon.svg` is the badge. Open `brand.html` (http://localhost:5173/brand.html) for the brand guide.

## Making an admin
Register on the site, then promote that account once:
```
python backend/create_admin.py you@example.com
```
Log in again; an **Admin** item appears in the sidebar (create/edit/publish lessons, see students and stats). Lessons are unpublished, never deleted, so student progress stays intact. Admin HTML is sanitised to a small tag allowlist.

## Security notes
- Passwords hashed with scrypt; JWT bearer auth; auth and submission endpoints rate-limited per IP (in memory – use Redis with several workers).
- The client never sends XP or pass/fail; the server grades, enforces lesson order and awards XP once (unique DB constraint).
- Set a real `SECRET_KEY` in production and restrict `CORS_ORIGINS` to your frontend URL.

## Not built yet
A Python (or other) runtime, Alembic migrations (tables are auto-created), deployment config, token revocation.
