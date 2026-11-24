"""Creates local TEST accounts for development only. Never run against production.
    python backend/seed_dev.py
"""
from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import User
from app.security import hash_password
from app.services.lessons import seed_lessons

ACCOUNTS = [
    {"username": "student", "email": "student@test.local", "password": "password", "role": "student"},
    {"username": "admin", "email": "admin@test.local", "password": "Admin#12345", "role": "admin"},
]

Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed_lessons(db)
    for a in ACCOUNTS:
        if db.scalar(select(User.id).where(User.email == a["email"])):
            print("exists:", a["email"])
            continue
        db.add(User(username=a["username"], email=a["email"], password_hash=hash_password(a["password"]), role=a["role"]))
        print("created:", a["email"])
    db.commit()
