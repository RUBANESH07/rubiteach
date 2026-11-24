from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (register tables)
from .config import settings
from .db import Base, SessionLocal, engine
from .routers import admin, auth, learning
from .services.lessons import seed_lessons


def _ensure_columns():
    """Tiny dev-time migration for databases created before a column existed. Use Alembic in production."""
    from sqlalchemy import inspect, text
    wanted = {
        "users": {"is_active": "BOOLEAN NOT NULL DEFAULT TRUE"},
        "courses": {"unlock_mode": "VARCHAR(20) NOT NULL DEFAULT 'sequential'"},
        "lessons": {"tests": "JSON"},
    }
    insp = inspect(engine)
    for table, cols in wanted.items():
        have = {c["name"] for c in insp.get_columns(table)}
        for name, ddl in cols.items():
            if name not in have:
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Dev convenience. For PostgreSQL in production manage the schema with Alembic migrations.
    Base.metadata.create_all(engine)
    _ensure_columns()
    with SessionLocal() as db:
        seed_lessons(db)
    yield


app = FastAPI(title="SQL Academy API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


app.include_router(auth.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
