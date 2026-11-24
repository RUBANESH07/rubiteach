from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Achievement, HintUsage, Lesson, LessonProgress, User, XpTransaction
from . import lessons as lesson_svc

BADGES = {
    "first": lambda s: s["count"] >= 1,
    "five": lambda s: s["count"] >= 5,
    "xp100": lambda s: s["xp"] >= 100,
    "join": lambda s: 10 in s["done"],
    "streak3": lambda s: s["streak"] >= 3,
    "window": lambda s: 15 in s["done"],
    "all": lambda s: s["courses_done"] >= 1,
}


def level(xp: int) -> int:
    return xp // 100 + 1


def completed(db: Session, user: User) -> dict[int, int]:
    rows = db.execute(select(LessonProgress.lesson_id, LessonProgress.xp_awarded).where(LessonProgress.user_id == user.id))
    return {lid: xp for lid, xp in rows}


def badge_ids(db: Session, user: User) -> list[str]:
    return list(db.scalars(select(Achievement.badge_id).where(Achievement.user_id == user.id)))


def _touch_streak(user: User, today: date):
    if user.last_active_day == today:
        return
    user.streak = user.streak + 1 if user.last_active_day == today - timedelta(days=1) else 1
    user.last_active_day = today


def award_completion(db: Session, user: User, lesson: Lesson, today: date | None = None) -> tuple[int, list[str]]:
    """Award XP once per lesson. Returns (xp_awarded_now, newly_unlocked_badges)."""
    today = today or date.today()
    lesson_id = lesson.id
    if db.scalar(select(LessonProgress.id).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id)):
        return 0, []
    used_hint = db.scalar(select(HintUsage.id).where(HintUsage.user_id == user.id, HintUsage.lesson_id == lesson_id)) is not None
    base = lesson.xp
    points = -(-base // 2) if used_hint else base
    try:
        with db.begin_nested():
            db.add(LessonProgress(user_id=user.id, lesson_id=lesson_id, xp_awarded=points))
            db.add(XpTransaction(user_id=user.id, points=points, reason="lesson_complete", lesson_id=lesson_id))
            db.flush()
    except IntegrityError:  # concurrent duplicate request already rewarded this lesson
        return 0, []
    user.xp += points
    _touch_streak(user, today)
    new = _unlock_badges(db, user)
    db.commit()
    return points, new


def _courses_done(db: Session, done: dict) -> int:
    by_course: dict[int, list[int]] = {}
    for l in lesson_svc.published(db):
        by_course.setdefault(l.course_id, []).append(l.id)
    return sum(1 for ids in by_course.values() if all(i in done for i in ids))


def _unlock_badges(db: Session, user: User) -> list[str]:
    done = completed(db, user)
    snap = {"count": len(done), "xp": user.xp, "streak": user.streak, "done": done, "courses_done": _courses_done(db, done)}
    have, new = set(badge_ids(db, user)), []
    for bid, test in BADGES.items():
        if bid not in have and test(snap):
            db.add(Achievement(user_id=user.id, badge_id=bid))
            new.append(bid)
    return new


def leaderboard(db: Session, limit: int = 10):
    q = select(User.username, User.xp, User.streak).where(User.role == "student", User.is_active.is_(True)).order_by(User.xp.desc(), User.username).limit(limit)
    return [{"rank": i + 1, "username": u, "xp": x, "streak": s} for i, (u, x, s) in enumerate(db.execute(q))]


def total_users(db: Session) -> int:
    return db.scalar(select(func.count(User.id))) or 0
