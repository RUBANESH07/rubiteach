"""Validate course content files.   python backend/validate_course.py python [level3.json ...]

For every lesson: required fields exist, the reference solution runs and passes its own tests, the starter
code does NOT already pass, any `requires` words appear in the solution, and hints are present.
Exit code 1 if anything fails.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent))
from app.pyrunner import grade, validate  # noqa: E402

ROOT = Path(__file__).parent / "app" / "content" / "courses"
ALLOWED_TAGS = ("b", "i", "em", "strong", "code", "br", "p", "ul", "ol", "li")
REQUIRED = ("title", "concept", "why", "example", "example_note", "prompt", "starter", "solution", "hints", "tests")


def check_html(field, text, problems, label):
    import re
    for m in re.finditer(r"<(/?)([a-zA-Z0-9]+)", text):
        if m.group(2).lower() not in ALLOWED_TAGS:
            problems.append(f"{label}: <{m.group(2)}> not allowed in {field}")
    if re.search(r"<(?!/?(?:%s)\b)" % "|".join(ALLOWED_TAGS), text):
        problems.append(f"{label}: raw '<' in {field}; write &lt; instead")


def main():
    slug = sys.argv[1]
    folder = ROOT / slug
    files = [folder / f for f in sys.argv[2:]] or sorted(folder.glob("level*.json"))
    bad = total = 0
    for f in files:
        level = json.loads(f.read_text(encoding="utf-8"))
        print(f"== {f.name}: {level['title']} ({len(level['lessons'])} lessons)")
        for i, les in enumerate(level["lessons"], 1):
            total += 1
            label = f"{f.name}#{i} {les.get('title', '?')}"
            problems = []
            for k in REQUIRED:
                if not les.get(k) and k != "starter":
                    problems.append(f"missing {k}")
            if not problems:
                for fld in ("concept", "why", "prompt", "example_note"):
                    check_html(fld, les[fld], problems, label)
                if not isinstance(les["tests"], dict) or not les["tests"].get("cases"):
                    problems.append("tests.cases must be a non-empty list")
                if not 2 <= len(les["hints"]) <= 4:
                    problems.append("need 2-4 hints")
                msg = validate(les)
                if msg:
                    problems.append(f"validate: {msg}")
                else:
                    ok, why = grade(SimpleNamespace(**les), les["solution"])
                    if not ok:
                        problems.append(f"solution does not pass own tests: {why}")
                    ok, _ = grade(SimpleNamespace(**les), les["starter"])
                    if ok:
                        problems.append("starter code already passes (task would be free XP)")
                    ok, _ = grade(SimpleNamespace(**les), "pass")
                    if ok:
                        problems.append("an empty program ('pass') passes")
            if problems:
                bad += 1
                print(f"  FAIL {label}")
                for p in problems:
                    print("       -", p)
    print(f"\n{total - bad}/{total} lessons OK")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
