from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut
from ..security import auth_limiter, create_token, current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# Verifying against a dummy hash keeps login timing similar whether or not the email exists.
_DUMMY = hash_password("not-a-real-password")


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth_limiter)])
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User.id).where((User.email == email) | (User.username == body.username))):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username or email is already registered.")
    user = User(username=body.username, email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    return TokenOut(access_token=create_token(user), user=user)


@router.post("/login", response_model=TokenOut, dependencies=[Depends(auth_limiter)])
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    ok = verify_password(body.password, user.password_hash if user else _DUMMY)
    if not user or not ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been disabled. Contact an administrator.")
    return TokenOut(access_token=create_token(user), user=user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(_: User = Depends(current_user)):
    # Tokens are stateless; the client discards its token. Add a denylist here if you need revocation.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
