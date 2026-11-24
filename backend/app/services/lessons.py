import json
import re
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Course, Lesson, LessonProgress, Module

SEED_FILE = Path(__file__).parent.parent / "content" / "lessons.json"
COURSES_DIR = Path(__file__).parent.parent / "content" / "courses"
PUBLIC_FIELDS = ("id", "course_id", "module_id", "position", "title", "minutes", "xp", "concept", "why",
                 "example_sql", "example_note", "prompt", "starter", "ordered")

SEED_MODULES = {
    "m1": ("Foundations", "Read data from a table."),
    "m2": ("Sorting & shaping", "Control the order and size of results."),
    "m3": ("Summarising data", "Count, total, average and group."),
    "m4": ("Combining tables", "Join related data together."),
    "m5": ("Advanced queries", "CASE, CTEs and window functions."),
    "m6": ("Changing data", "INSERT, UPDATE and DELETE safely."),
}

_TAGS = "b|i|em|strong|code|br|p|ul|ol|li"
_TAG_RE = re.compile(rf"<(/?)({_TAGS})\s*/?>", re.I)


def sanitize_html(text: str) -> str:
    """Allow a few attribute-less formatting tags; escape everything else (XSS protection for admin input)."""
    out, pos = [], 0
    for m in _TAG_RE.finditer(text):
        out.append(_escape(text[pos:m.start()]))
        out.append(f"<{m.group(1)}{m.group(2).lower()}>")
        pos = m.end()
    out.append(_escape(text[pos:]))
    return "".join(out)


def _escape(s: str) -> str:
    s = re.sub(r"&(?!#?\w+;)", "&amp;", s)  # keep existing entities such as &gt;
    return s.replace("<", "&lt;").replace(">", "&gt;")


def seed_lessons(db: Session) -> int:
    """Create the starter courses the first time the app runs (SQL), then any course folders under content/courses."""
    n = _seed_sql(db)
    return n + seed_course_folders(db)


def seed_course_folders(db: Session) -> int:
    """Load content/courses/<slug>/course.json + level*.json for every course that has no lessons yet."""
    added = 0
    if not COURSES_DIR.exists():
        return 0
    for folder in sorted(p for p in COURSES_DIR.iterdir() if (p / "course.json").exists()):
        meta = json.loads((folder / "course.json").read_text(encoding="utf-8"))
        course = db.scalar(select(Course).where(Course.slug == meta["slug"]))
        if course and db.scalar(select(func.count(Lesson.id)).where(Lesson.course_id == course.id)):
            continue
        levels = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(folder.glob("level*.json"))]
        if not levels:
            continue
        if not course:
            course = Course(slug=meta["slug"], position=meta.get("position", 99))
            db.add(course)
        course.title, course.icon, course.runtime = meta["title"], meta.get("icon", "📘"), meta["runtime"]
        course.description, course.unlock_mode = meta.get("description", ""), meta.get("unlock_mode", "sequential")
        course.published = meta.get("published", True)
        db.flush()
        for old in db.scalars(select(Module).where(Module.course_id == course.id)):
            db.delete(old)
        db.flush()
        pos = 0
        for mi, level in enumerate(levels, 1):
            mod = Module(course_id=course.id, title=level["title"], blurb=level.get("blurb", ""), position=mi)
            db.add(mod)
            db.flush()
            for les in level["lessons"]:
                pos += 1
                db.add(Lesson(course_id=course.id, module_id=mod.id, position=pos, published=True,
                              title=les["title"], minutes=les.get("minutes", 5), xp=les.get("xp", 10),
                              concept=les["concept"], why=les.get("why", ""), example_sql=les.get("example", ""),
                              example_note=les.get("example_note", ""), prompt=les["prompt"],
                              starter=les.get("starter", ""), solution=les["solution"], hints=les.get("hints", []),
                              tests=les.get("tests"), ordered=False))
                added += 1
        db.commit()
    return added


def _seed_sql(db: Session) -> int:
    if db.scalar(select(func.count(Course.id))):
        return 0
    course = Course(slug="sql", title="SQL", icon="🗄️", runtime="sql", position=1, published=True,
                    description="Query real data: SELECT, JOINs, aggregates, CTEs and window functions.")
    db.add(course)
    db.flush()
    mods = {}
    for i, (key, (title, blurb)) in enumerate(SEED_MODULES.items(), 1):
        mods[key] = Module(course_id=course.id, title=title, blurb=blurb, position=i)
        db.add(mods[key])
    db.flush()
    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    for row in data:
        row = dict(row)
        row["module_id"] = mods[row.pop("module")].id
        db.add(Lesson(**row, course_id=course.id, published=True))
    db.commit()
    return len(data)


def published(db: Session, course_id: int | None = None) -> list[Lesson]:
    q = (select(Lesson).join(Course, Course.id == Lesson.course_id)
         .where(Lesson.published.is_(True), Course.published.is_(True))
         .order_by(Course.position, Course.id, Lesson.position, Lesson.id))
    if course_id is not None:
        q = q.where(Lesson.course_id == course_id)
    return list(db.scalars(q))


def public_dict(l: Lesson) -> dict:
    return {f: getattr(l, f) for f in PUBLIC_FIELDS}


def previous_of(db: Session, lesson: Lesson) -> Lesson | None:
    """The lesson a student must finish first. Courses with unlock_mode 'by_module' open every module at once."""
    ordered = published(db, lesson.course_id)
    course = db.get(Course, lesson.course_id)
    if course and course.unlock_mode == "by_module":
        ordered = [l for l in ordered if l.module_id == lesson.module_id]
    for i, l in enumerate(ordered):
        if l.id == lesson.id:
            return ordered[i - 1] if i else None
    return None


def completed_ids(db: Session, user_id) -> set[int]:
    return set(db.scalars(select(LessonProgress.lesson_id).where(LessonProgress.user_id == user_id)))
