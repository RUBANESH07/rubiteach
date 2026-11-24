import base64
import hashlib
import hmac
import os
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import User

_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)
    return f"scrypt${base64.b64encode(salt).decode()}${base64.b64encode(h).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, h = stored.split("$")
        calc = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), n=_N, r=_R, p=_P, dklen=32)
        return hmac.compare_digest(calc, base64.b64decode(h))
    except Exception:
        return False


def create_token(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": str(user.id), "exp": exp}, settings.secret_key, algorithm="HS256")


_bearer = HTTPBearer(auto_error=False)


def current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer), db: Session = Depends(get_db)
) -> User:
    err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    if not cred:
        raise err
    try:
        uid = uuid.UUID(jwt.decode(cred.credentials, settings.secret_key, algorithms=["HS256"])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise err
    user = db.get(User, uid)
    if not user:
        raise err
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been disabled. Contact an administrator.")
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user


class RateLimiter:
    """Sliding-window limiter per client IP (in memory). Use Redis if you run several workers."""

    def __init__(self, limit: int, window: int):
        self.limit, self.window, self.hits = limit, window, defaultdict(deque)

    def __call__(self, request: Request):
        key = request.client.host if request.client else "unknown"
        q, t = self.hits[key], time.monotonic()
        while q and t - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests, slow down.")
        q.append(t)

    def reset(self):
        self.hits.clear()


auth_limiter = RateLimiter(limit=20, window=60)
submit_limiter = RateLimiter(limit=60, window=60)
run_limiter = RateLimiter(limit=40, window=60)
