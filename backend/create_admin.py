"""Promote an existing user to admin:  python create_admin.py you@example.com
Register the account through the site first, then run this once."""
import sys

from sqlalchemy import select

from app.db import SessionLocal
from app.models import User

if len(sys.argv) != 2:
    sys.exit("usage: python create_admin.py <email>")
with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == sys.argv[1].lower()))
    if not user:
        sys.exit("No user with that email. Register on the site first.")
    user.role = "admin"
    db.commit()
    print(f"{user.username} is now an admin.")
