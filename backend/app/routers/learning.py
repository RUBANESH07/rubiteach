from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Course, HintUsage, Lesson, Module, Submission, User
from ..runtimes import RUNTIMES
from ..pyrunner import run_python
from ..schemas import HintOut, ProgressOut, RunIn, RunOut, SubmissionIn, SubmissionOut
from ..security import current_user, run_limiter, submit_limiter
from ..services import gamification as gm
from ..services import lessons as svc

router = APIRouter(tags=["learning"])


def _progress(db: Session, user: User) -> ProgressOut:
    return ProgressOut(xp=user.xp, level=gm.level(user.xp), streak=user.streak,
                       completed=gm.completed(db, user), badges=gm.badge_ids(db, user))


def _lesson_for_student(db: Session, user: User, lesson_id: int) -> Lesson:
    lesson = db.get(Lesson, lesson_id)
    course = db.get(Course, lesson.course_id) if lesson else None
    if not lesson or not lesson.published or not course.published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found.")
    prev = svc.previous_of(db, lesson)
    if user.role != "admin" and prev and prev.id not in svc.completed_ids(db, user.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Complete the previous lesson first.")
    return lesson


@router.get("/courses")
def list_courses(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Published courses with their modules and lesson counts."""
    lessons = svc.published(db)
    done = svc.completed_ids(db, user.id)
    out = []
    for c in db.scalars(select(Course).where(Course.published.is_(True)).order_by(Course.position, Course.id)):
        mine = [l for l in lessons if l.course_id == c.id]
        mods = db.scalars(select(Module).where(Module.course_id == c.id).order_by(Module.position, Module.id))
        out.append({"id": c.id, "slug": c.slug, "title": c.title, "description": c.description, "icon": c.icon,
                    "runtime": c.runtime, "unlock_mode": c.unlock_mode, "lessons": len(mine), "completed": sum(1 for l in mine if l.id in done),
                    "modules": [{"id": m.id, "title": m.title, "blurb": m.blurb} for m in mods]})
    return out


@router.get("/lessons")
def list_lessons(course_id: int | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Published lessons for the learning UI, ordered course by course. Solutions and hints are never included."""
    return [svc.public_dict(l) for l in svc.published(db, course_id)]


@router.get("/progress", response_model=ProgressOut)
def progress(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _progress(db, user)


@router.post("/submissions", response_model=SubmissionOut, dependencies=[Depends(submit_limiter)])
def submit(body: SubmissionIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = _lesson_for_student(db, user, body.lesson_id)
    runtime = RUNTIMES.get(db.get(Course, lesson.course_id).runtime)
    if not runtime:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "This course type cannot be graded yet.")
    passed, message = runtime.grade(lesson, body.sql)
    db.add(Submission(user_id=user.id, lesson_id=lesson.id, sql=body.sql, passed=passed, message=message))
    db.commit()
    xp, new = gm.award_completion(db, user, lesson) if passed else (0, [])
    return SubmissionOut(passed=passed, message=message, xp_awarded=xp, new_badges=new, progress=_progress(db, user))


@router.post("/run", response_model=RunOut, dependencies=[Depends(run_limiter)])
def run_code(body: RunIn, user: User = Depends(current_user)):
    """Run (not grade) student code for runtimes that execute on the server. Earns no XP."""
    if body.runtime != "python" or "python" not in RUNTIMES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This runtime does not run on the server.")
    r = run_python(body.code, body.stdin)
    if not r.ok:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "The code runner is unavailable. Try again.")
    return RunOut(stdout=r.stdout, error=r.error, timed_out=r.timed_out, ms=r.ms)


@router.post("/lessons/{lesson_id}/hint", response_model=HintOut)
def next_hint(lesson_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Hints are served (and counted) by the server so the hint XP penalty cannot be skipped."""
    lesson = _lesson_for_student(db, user, lesson_id)
    hints = lesson.hints or []
    if not hints:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This lesson has no hints.")
    usage = db.scalar(select(HintUsage).where(HintUsage.user_id == user.id, HintUsage.lesson_id == lesson_id))
    if not usage:
        usage = HintUsage(user_id=user.id, lesson_id=lesson_id, level=0)
        db.add(usage)
    usage.level = min((usage.level or 0) + 1, len(hints))
    db.commit()
    return HintOut(level=usage.level, total=len(hints), hint=hints[usage.level - 1])


@router.get("/hints/{lesson_id}", response_model=list[str])
def revealed_hints(lesson_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = _lesson_for_student(db, user, lesson_id)
    usage = db.scalar(select(HintUsage).where(HintUsage.user_id == user.id, HintUsage.lesson_id == lesson_id))
    return (lesson.hints or [])[: usage.level] if usage else []


@router.get("/achievements")
def achievements(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"unlocked": gm.badge_ids(db, user), "all": list(gm.BADGES)}


@router.get("/leaderboard")
def leaderboard(limit: int = Query(10, ge=1, le=50), user: User = Depends(current_user), db: Session = Depends(get_db)):
    return gm.leaderboard(db, limit)
