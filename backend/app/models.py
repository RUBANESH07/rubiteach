import uuid
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def now() -> datetime:
    return datetime.now(timezone.utc)


def _created():
    return mapped_column(DateTime(timezone=True), default=now)


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(20), default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    xp: Mapped[int] = mapped_column(Integer, default=0, index=True)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_day: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = _created()


class Course(Base):
    """A technology course. `runtime` decides how tasks run and are graded (only 'sql' exists so far)."""

    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(300), default="")
    icon: Mapped[str] = mapped_column(String(8), default="📘")
    runtime: Mapped[str] = mapped_column(String(20), default="sql")
    unlock_mode: Mapped[str] = mapped_column(String(20), default="sequential", server_default="sequential")
    position: Mapped[int] = mapped_column(Integer, default=0, index=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = _created()


class Module(Base):
    __tablename__ = "modules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(80))
    blurb: Mapped[str] = mapped_column(String(200), default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = _created()


class Lesson(Base):
    """Lesson content managed by admins. Integer ids keep progress rows and URLs simple."""

    __tablename__ = "lessons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    position: Mapped[int] = mapped_column(Integer, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    minutes: Mapped[int] = mapped_column(Integer, default=5)
    xp: Mapped[int] = mapped_column(Integer, default=10)
    concept: Mapped[str] = mapped_column(Text, default="")
    why: Mapped[str] = mapped_column(Text, default="")
    example_sql: Mapped[str] = mapped_column(Text, default="")
    example_note: Mapped[str] = mapped_column(Text, default="")
    prompt: Mapped[str] = mapped_column(Text, default="")
    starter: Mapped[str] = mapped_column(Text, default="")
    solution: Mapped[str] = mapped_column(Text)
    verify: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordered: Mapped[bool] = mapped_column(Boolean, default=False)
    hints: Mapped[list] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), default=list)
    tests: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = _created()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Submission(Base):
    __tablename__ = "submissions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(Integer)
    sql: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(Boolean)
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = _created()
    __table_args__ = (Index("ix_submissions_user_lesson", "user_id", "lesson_id"),)


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(Integer)
    xp_awarded: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = _created()
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),)


class HintUsage(Base):
    __tablename__ = "hint_usage"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = _created()
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_hint_user_lesson"),)


class XpTransaction(Base):
    """Append-only ledger. The unique key makes a duplicate reward impossible, even under races."""

    __tablename__ = "xp_transactions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(50))
    lesson_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = _created()
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", "reason", name="uq_xp_once"),)


class Achievement(Base):
    __tablename__ = "achievements"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    badge_id: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = _created()
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_badge_user"),)
