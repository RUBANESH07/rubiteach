# Authoring Python lessons

Each course lives in `content/courses/<slug>/`: `course.json` plus `level1.json … levelN.json`
(one file = one module). Validate with `python backend/validate_course.py python level3.json`.
Author the JSON by generating it from a Python script (triple-quoted strings) to avoid escaping mistakes.

## Level file
```json
{ "title": "Level 3 · Data Structures", "blurb": "one sentence", "lessons": [ <lesson>, ... ] }
```

## Lesson
| field | rules |
|---|---|
| title | the syllabus topic name (short) |
| minutes, xp | minutes 4-12; xp 10 (L1-2), 15 (L3-4), 20 (L5-6), 25 (L7), 30 (L8) |
| concept | 2-4 sentences, plain English for a complete beginner. Tags allowed: b, i, em, strong, code, br, p, ul, ol, li. Write `&lt;` `&gt;` `&amp;` for those characters. |
| why | 1-2 sentences: where this is used in real programs |
| example | a small runnable code snippet that PRINTS something (the student can run it with one click) |
| example_note | one sentence saying what the example shows/prints |
| prompt | the task, using `<code>` for names. Say exactly what to print or which function to write. |
| starter | scaffold code with a `# comment` guide. It must NOT already pass. |
| solution | reference solution (private) |
| hints | 2-4 progressively stronger hints (plain text, last hint nearly gives the answer) |
| tests | `{"cases": [...], "requires": [...], "forbid": [...]}` |

## Tests
Expected results are **computed by running your `solution`**, so you never write expected values.
A case is `{"stdin": "...", "expr": "...", "visible": true|false, "check_stdout": false, "note": "..."}`.
* **Output task** (student prints): cases only set `stdin` (omit for none). stdout is compared (trailing spaces ignored).
* **Function task** (student defines a function/class): set `expr`, e.g. `"add(2, 3)"`. The expression is evaluated after the
  student code runs and its `repr()` is compared. Make results deterministic (sort sets/dicts, no memory addresses, no time/random).
  Printed text is ignored unless `"check_stdout": true`.
* Use 2-5 cases. The FIRST case is visible to students (expected vs got is shown); other cases should be `"visible": false` hidden edge cases.
* `requires`: words that must appear in the student code to teach the topic (e.g. `["lambda"]`, `["while"]`). `forbid`: words that must not.
* The solution must print something or have `expr`. Never use `input()` unless every case supplies `stdin`.

## Sandbox limits (tasks must work inside them)
5 second limit per run. No network, no subprocesses/multiprocessing processes, no files outside a temporary working folder
(reading and writing files in the current folder IS allowed, so file/JSON/CSV tasks work). `threading`, `asyncio`, `json`, `csv`,
`re`, `collections`, `functools`, `itertools`, `dataclasses`, `abc`, `copy`, `typing` and the rest of the standard library work.
Output is capped at 100k characters. No third-party packages, no randomness or time in graded output.

## Style (academy point of view)
Teach, don't test: one idea per lesson, build on earlier lessons, friendly second person ("you"), real-world examples
(shopping bills, marks, bank accounts), and a task that is small enough to finish in 5 minutes.
