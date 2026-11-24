import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Achievement, Course, HintUsage, Lesson, LessonProgress, Module, Submission, User, XpTransaction
from ..runtimes import PLANNED, RUNTIMES
from ..security import hash_password, require_admin
from ..services import lessons as svc

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
UNPROCESSABLE = 422


def _422(msg: str):
    return HTTPException(UNPROCESSABLE, msg)


# ---------------------------------------------------------------- courses
class CourseIn(BaseModel):
    slug: str = Field(min_length=2, max_length=40, pattern=r"^[a-z0-9][a-z0-9-]*$")
    title: str = Field(min_length=2, max_length=80)
    description: str = Field("", max_length=300)
    icon: str = Field("📘", max_length=8)
    runtime: str
    unlock_mode: str = Field("sequential", pattern="^(sequential|by_module)$")
    position: int | None = Field(None, ge=1)
    published: bool = False


class PublishIn(BaseModel):
    published: bool


def _course_out(c: Course) -> dict:
    return {"id": c.id, "slug": c.slug, "title": c.title, "description": c.description, "icon": c.icon,
            "runtime": c.runtime, "unlock_mode": c.unlock_mode, "position": c.position, "published": c.published,
            "runtime_available": c.runtime in RUNTIMES}


def _check_course(body: CourseIn) -> dict:
    data = body.model_dump()
    data["title"] = svc.sanitize_html(data["title"])
    data["description"] = svc.sanitize_html(data["description"])
    if data["published"] and body.runtime not in RUNTIMES:
        raise _422(f"Runtime '{body.runtime}' is not available yet, so this course cannot be published.")
    return data


@router.get("/runtimes")
def runtimes():
    return {"available": [{"key": r.key, "label": r.label} for r in RUNTIMES.values()], "planned": PLANNED}


@router.get("/courses")
def list_courses(db: Session = Depends(get_db)):
    return [_course_out(c) for c in db.scalars(select(Course).order_by(Course.position, Course.id))]


@router.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(body: CourseIn, db: Session = Depends(get_db)):
    data = _check_course(body)
    if data["position"] is None:
        data["position"] = (db.scalar(select(func.max(Course.position))) or 0) + 1
    course = Course(**data)
    db.add(course)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "A course with that slug already exists.")
    return _course_out(course)


@router.put("/courses/{course_id}")
def update_course(course_id: int, body: CourseIn, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    data = _check_course(body)
    data["position"] = data["position"] or course.position
    for k, v in data.items():
        setattr(course, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "A course with that slug already exists.")
    return _course_out(course)


@router.post("/courses/{course_id}/publish")
def publish_course(course_id: int, body: PublishIn, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found.")
    if body.published and course.runtime not in RUNTIMES:
        raise _422(f"Runtime '{course.runtime}' is not available yet, so this course cannot be published.")
    course.published = body.published
    db.commit()
    return _course_out(course)


# ---------------------------------------------------------------- modules
class ModuleIn(BaseModel):
    course_id: int
    title: str = Field(min_length=2, max_length=80)
    blurb: str = Field("", max_length=200)
    position: int | None = Field(None, ge=1)


def _module_out(m: Module) -> dict:
    return {"id": m.id, "course_id": m.course_id, "title": m.title, "blurb": m.blurb, "position": m.position}


@router.get("/modules")
def list_modules(course_id: int | None = None, db: Session = Depends(get_db)):
    q = select(Module).order_by(Module.course_id, Module.position, Module.id)
    if course_id is not None:
        q = q.where(Module.course_id == course_id)
    return [_module_out(m) for m in db.scalars(q)]


@router.post("/modules", status_code=status.HTTP_201_CREATED)
def create_module(body: ModuleIn, db: Session = Depends(get_db)):
    if not db.get(Course, body.course_id):
        raise _422("Unknown course.")
    pos = body.position or (db.scalar(select(func.max(Module.position)).where(Module.course_id == body.course_id)) or 0) + 1
    m = Module(course_id=body.course_id, title=svc.sanitize_html(body.title), blurb=svc.sanitize_html(body.blurb), position=pos)
    db.add(m)
    db.commit()
    return _module_out(m)


@router.put("/modules/{module_id}")
def update_module(module_id: int, body: ModuleIn, db: Session = Depends(get_db)):
    m = db.get(Module, module_id)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Module not found.")
    if body.course_id != m.course_id:
        raise _422("A module cannot move to another course.")
    m.title, m.blurb = svc.sanitize_html(body.title), svc.sanitize_html(body.blurb)
    m.position = body.position or m.position
    db.commit()
    return _module_out(m)


# ---------------------------------------------------------------- lessons
class LessonIn(BaseModel):
    module_id: int
    title: str = Field(min_length=3, max_length=120)
    minutes: int = Field(5, ge=1, le=120)
    xp: int = Field(10, ge=1, le=500)
    concept: str = Field(max_length=5000)
    why: str = Field("", max_length=2000)
    example_sql: str = Field("", max_length=3000)
    example_note: str = Field("", max_length=500)
    prompt: str = Field(min_length=3, max_length=2000)
    starter: str = Field("", max_length=3000)
    solution: str = Field(min_length=1, max_length=5000)
    verify: str | None = Field(None, max_length=5000)
    ordered: bool = False
    hints: list[str] = Field(default_factory=list, max_length=6)
    tests: dict | None = None
    published: bool = False
    position: int | None = Field(None, ge=1)


def _clean(body: LessonIn, db: Session) -> dict:
    module = db.get(Module, body.module_id)
    if not module:
        raise _422("Unknown module.")
    course = db.get(Course, module.course_id)
    runtime = RUNTIMES.get(course.runtime)
    if not runtime:
        raise _422(f"Course runtime '{course.runtime}' is not available yet, so its lessons cannot be saved.")
    data = body.model_dump()
    data["course_id"] = course.id
    for f in ("concept", "why", "prompt", "example_note", "title"):
        data[f] = svc.sanitize_html(data[f])
    data["hints"] = [svc.sanitize_html(h) for h in data["hints"] if h.strip()]
    data["verify"] = (data["verify"] or "").strip() or None
    # The reference solution must run and return something, otherwise nobody could ever pass.
    problem = runtime.validate(data)
    if problem:
        raise _422(problem)
    return data


def _full(l: Lesson) -> dict:
    return {**svc.public_dict(l), "solution": l.solution, "verify": l.verify, "hints": l.hints or [], "tests": l.tests, "published": l.published}


@router.get("/lessons")
def all_lessons(course_id: int | None = None, db: Session = Depends(get_db)):
    q = select(Lesson).order_by(Lesson.course_id, Lesson.position, Lesson.id)
    if course_id is not None:
        q = q.where(Lesson.course_id == course_id)
    return [_full(l) for l in db.scalars(q)]


@router.post("/lessons", status_code=status.HTTP_201_CREATED)
def create_lesson(body: LessonIn, db: Session = Depends(get_db)):
    data = _clean(body, db)
    if data["position"] is None:
        data["position"] = (db.scalar(select(func.max(Lesson.position)).where(Lesson.course_id == data["course_id"])) or 0) + 1
    lesson = Lesson(**data)
    db.add(lesson)
    db.commit()
    return _full(lesson)


@router.put("/lessons/{lesson_id}")
def update_lesson(lesson_id: int, body: LessonIn, db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found.")
    data = _clean(body, db)
    if data["course_id"] != lesson.course_id:
        raise _422("A lesson cannot move to another course.")
    data["position"] = data["position"] or lesson.position
    for k, v in data.items():
        setattr(lesson, k, v)
    db.commit()
    return _full(lesson)


@router.post("/lessons/{lesson_id}/publish")
def set_published(lesson_id: int, body: PublishIn, db: Session = Depends(get_db)):
    """Lessons are unpublished rather than deleted so student progress and XP history stay intact."""
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found.")
    lesson.published = body.published
    db.commit()
    return _full(lesson)


@router.post("/lessons/{lesson_id}/check")
def self_check(lesson_id: int, db: Session = Depends(get_db)):
    """Confirms the stored solution grades as correct against itself."""
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found.")
    runtime = RUNTIMES[db.get(Course, lesson.course_id).runtime]
    ok, msg = runtime.grade(lesson, lesson.solution)
    return {"ok": ok, "message": msg}


# ---------------------------------------------------------------- students & stats
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)
    role: str = Field("student", pattern="^(student|admin)$")


class RoleIn(BaseModel):
    role: str = Field(pattern="^(student|admin)$")


class ActiveIn(BaseModel):
    active: bool


class PasswordIn(BaseModel):
    password: str = Field(min_length=8, max_length=128)


def _user_out(u: User, done: int = 0) -> dict:
    return {"id": str(u.id), "username": u.username, "email": u.email, "role": u.role, "is_active": u.is_active,
            "xp": u.xp, "streak": u.streak, "lessons_completed": done, "last_active": u.last_active_day, "joined": u.created_at}


def _target(db: Session, user_id: str) -> User:
    try:
        u = db.get(User, uuid.UUID(user_id))
    except ValueError:
        u = None
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    return u


def _guard_admin_lockout(db: Session, me: User, target: User, action: str):
    """Stop admins locking everyone out: no self-demotion/disable/delete, never remove the last active admin."""
    if target.id == me.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"You cannot {action} your own account.")
    if target.role == "admin":
        others = db.scalar(select(func.count(User.id)).where(User.role == "admin", User.is_active.is_(True), User.id != target.id))
        if not others:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot remove the last active admin.")


def _wipe_progress(db: Session, u: User):
    for model in (LessonProgress, HintUsage, XpTransaction, Achievement):
        db.execute(delete(model).where(model.user_id == u.id))
    u.xp, u.streak, u.last_active_day = 0, 0, None


@router.get("/students")
def students(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(User.id)))
    done = dict(db.execute(select(LessonProgress.user_id, func.count()).group_by(LessonProgress.user_id)).all())
    rows = db.scalars(select(User).order_by(User.xp.desc(), User.username).offset((page - 1) * per_page).limit(per_page))
    return {"total": total, "page": page, "per_page": per_page, "items": [_user_out(u, done.get(u.id, 0)) for u in rows]}


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User.id).where((User.email == email) | (User.username == body.username))):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username or email is already registered.")
    u = User(username=body.username, email=email, password_hash=hash_password(body.password), role=body.role)
    db.add(u)
    db.commit()
    return _user_out(u)


@router.post("/users/{user_id}/role")
def set_role(user_id: str, body: RoleIn, me: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = _target(db, user_id)
    if body.role != "admin":
        _guard_admin_lockout(db, me, u, "demote")
    u.role = body.role
    db.commit()
    return _user_out(u)


@router.post("/users/{user_id}/active")
def set_active(user_id: str, body: ActiveIn, me: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = _target(db, user_id)
    if not body.active:
        _guard_admin_lockout(db, me, u, "disable")
    u.is_active = body.active
    db.commit()
    return _user_out(u)


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: str, body: PasswordIn, db: Session = Depends(get_db)):
    u = _target(db, user_id)
    u.password_hash = hash_password(body.password)
    db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/reset-progress")
def reset_progress(user_id: str, db: Session = Depends(get_db)):
    u = _target(db, user_id)
    _wipe_progress(db, u)
    db.commit()
    return _user_out(u)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, me: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = _target(db, user_id)
    _guard_admin_lockout(db, me, u, "delete")
    _wipe_progress(db, u)
    db.execute(delete(Submission).where(Submission.user_id == u.id))
    db.delete(u)
    db.commit()


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    subs = db.scalar(select(func.count(Submission.id)))
    passed = db.scalar(select(func.count(Submission.id)).where(Submission.passed.is_(True)))
    completions = dict(db.execute(select(LessonProgress.lesson_id, func.count()).group_by(LessonProgress.lesson_id)).all())
    attempts = dict(db.execute(select(Submission.lesson_id, func.count()).group_by(Submission.lesson_id)).all())
    titles = {c.id: c.title for c in db.scalars(select(Course))}
    return {
        "students": db.scalar(select(func.count(User.id)).where(User.role == "student")),
        "submissions": subs, "pass_rate": round(passed / subs, 3) if subs else None,
        "lessons": [{"id": l.id, "title": l.title, "course": titles.get(l.course_id), "published": l.published,
                     "completions": completions.get(l.id, 0), "attempts": attempts.get(l.id, 0)}
                    for l in db.scalars(select(Lesson).order_by(Lesson.course_id, Lesson.position, Lesson.id))],
    }
