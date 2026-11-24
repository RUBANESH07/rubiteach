"""Generates level5.json. Run: python gen_level5.py"""
import json
from pathlib import Path

L = []


def lesson(**kw):
    kw.setdefault("minutes", 6)
    kw.setdefault("xp", 20)
    L.append(kw)


def vis(expr, visible=False):
    return {"expr": expr, "visible": visible}


lesson(
    title="List Comprehension",
    concept="A <b>list comprehension</b> builds a new list in one line: <code>[expression for item in items if condition]</code>. "
            "It is a short form of a loop that appends to a list. The <code>if</code> part is optional and keeps only matching items.",
    why="Cleaning and transforming lists of data is a daily job, and comprehensions make it short and readable.",
    example=r"""nums = [1, 2, 3, 4, 5]
print([n * 10 for n in nums])
print([n for n in nums if n % 2 == 1])""",
    example_note="Multiplies every number by 10, then keeps only the odd ones.",
    prompt="Write <code>squares_of_evens(nums)</code> that returns a list of the squares of only the even numbers, using a list comprehension (no <code>append</code>).",
    starter=r"""def squares_of_evens(nums):
    # return [... for n in nums if ...]
    pass
""",
    solution=r"""def squares_of_evens(nums):
    return [n * n for n in nums if n % 2 == 0]""",
    hints=["Shape: [what_to_keep for n in nums if condition].", "Even means n % 2 == 0.", "return [n * n for n in nums if n % 2 == 0]"],
    tests={"cases": [vis("squares_of_evens([1, 2, 3, 4, 5, 6])", True), vis("squares_of_evens([])"), vis("squares_of_evens([1, 3, 5])"), vis("squares_of_evens([0, -2])")], "requires": [" for ", " in "], "forbid": ["append"]},
)
lesson(
    title="Dictionary Comprehension",
    concept="A <b>dictionary comprehension</b> builds a dict in one line using curly braces and a <code>key: value</code> pair: <code>{word: len(word) for word in words}</code>. It works just like a list comprehension.",
    why="Turning a list into a lookup table, like name to score or product to price, is very common.",
    example=r"""fruits = ['apple', 'fig']
print({f: len(f) for f in fruits})""",
    example_note="Maps each fruit to the length of its name.",
    prompt="Write <code>name_lengths(names)</code> that returns a dictionary mapping each name to its length, using a dictionary comprehension.",
    starter=r"""def name_lengths(names):
    # return {key: value for ... in names}
    pass
""",
    solution=r"""def name_lengths(names):
    return {name: len(name) for name in names}""",
    hints=["Curly braces with key: value, then for ... in names.", "The key is the name, the value is len(name).", "return {name: len(name) for name in names}"],
    tests={"cases": [vis("name_lengths(['Asha', 'Ravi', 'Meenakshi'])", True), vis("name_lengths([])"), vis("name_lengths(['Al', 'Al'])")], "requires": [" for ", "{"], "forbid": ["dict("]},
)
lesson(
    title="Set Comprehension",
    concept="A <b>set comprehension</b> looks like a dictionary one but with a single value: <code>{x for x in items}</code>. A set keeps each value only once, so duplicates disappear automatically.",
    why="Finding the unique cities, tags or first letters in a pile of data is a set job.",
    example=r"""words = ['apple', 'avocado', 'banana']
print(sorted({w[0] for w in words}))""",
    example_note="Collects the unique first letters (sorted so the output is stable).",
    prompt="Write <code>unique_first_letters(words)</code> that returns a <b>set</b> of the lowercase first letters of the words, using a set comprehension.",
    starter=r"""def unique_first_letters(words):
    # return {... for w in words}
    pass
""",
    solution=r"""def unique_first_letters(words):
    return {w[0].lower() for w in words}""",
    hints=["Use curly braces with one expression and a for.", "w[0] is the first letter; .lower() makes it lowercase.", "return {w[0].lower() for w in words}"],
    tests={"cases": [vis("sorted(unique_first_letters(['apple', 'Avocado', 'banana']))", True), vis("sorted(unique_first_letters([]))"), vis("sorted(unique_first_letters(['Zed', 'zoo', 'Yak']))"), vis("type(unique_first_letters(['a'])).__name__")], "requires": [" for ", "{"], "forbid": ["set("]},
)
lesson(
    title="Generator Expression",
    concept="A <b>generator expression</b> is a comprehension in round brackets: <code>(x * x for x in range(5))</code>. It does not build a list; it produces values one at a time when asked, which saves memory. "
            "Functions like <code>sum()</code> accept it directly: <code>sum(x for x in nums)</code>.",
    why="When data is huge (millions of rows), a generator avoids storing everything at once.",
    example=r"""squares = (n * n for n in range(1, 4))
print(next(squares))
print(sum(n * n for n in range(1, 4)))""",
    example_note="Takes one value from a generator, then sums another one.",
    prompt="Write <code>sum_of_squares(n)</code> that returns <code>1*1 + 2*2 + ... + n*n</code> using <code>sum()</code> with a generator expression (do not build a list with square brackets).",
    starter=r"""def sum_of_squares(n):
    # sum(... for i in range(...))
    pass
""",
    solution=r"""def sum_of_squares(n):
    return sum(i * i for i in range(1, n + 1))""",
    hints=["range(1, n + 1) gives 1 up to n.", "Pass the generator straight into sum(...).", "return sum(i * i for i in range(1, n + 1))"],
    tests={"cases": [vis("sum_of_squares(3)", True), vis("sum_of_squares(0)"), vis("sum_of_squares(1)"), vis("sum_of_squares(100)")], "requires": ["sum(", " for "], "forbid": ["["]},
)
lesson(
    title="Modules (import, custom modules)", minutes=7,
    concept="A <b>module</b> is a file of ready-made Python code. Load it with <code>import math</code> and use its tools as <code>math.sqrt(16)</code>. "
            "Python ships with many (<code>math</code>, <code>statistics</code>, <code>random</code>). Your own file <code>tools.py</code> is also a module: <code>import tools</code>.",
    why="Modules let you reuse tested code instead of writing everything yourself, and keep big projects organised in files.",
    example=r"""import math
import statistics

print(math.sqrt(49))
print(statistics.mean([2, 4, 9]))""",
    example_note="Imports two standard modules and uses one function from each.",
    prompt="Read one line of space-separated numbers. Import <code>statistics</code> and <code>math</code>, then print the mean on the first line and the mean rounded <b>down</b> (<code>math.floor</code>) on the second. Example: <code>10 20 30</code> prints <code>20.0</code> then <code>20</code>.",
    starter=r"""# import statistics and math here

nums = [float(x) for x in input().split()]
# print the mean, then the floor of the mean
""",
    solution=r"""import statistics
import math

nums = [float(x) for x in input().split()]
mean = statistics.mean(nums)
print(mean)
print(math.floor(mean))""",
    hints=["Put import statistics and import math at the top.", "statistics.mean(nums) gives the average.", "Print the mean, then print(math.floor(mean))."],
    tests={"cases": [{"stdin": "10 20 30\n"}, {"stdin": "1 2\n", "visible": False}, {"stdin": "7\n", "visible": False}, {"stdin": "2.5 3.5 9\n", "visible": False}], "requires": ["import", "statistics.", "math."]},
)
lesson(
    title="Packages",
    concept="A <b>package</b> is a folder of modules, with a file named <code>__init__.py</code> marking it as a package. "
            "Inside it modules can be grouped, e.g. <code>shop/billing.py</code> is imported as <code>import shop.billing</code> or <code>from shop import billing</code>. "
            "The standard library has packages too: <code>os</code> is a package and <code>os.path</code> is a module inside it.",
    why="Packages organise large projects into folders, and almost every third-party library you install is a package.",
    example=r"""import os.path

print(os.path.basename('notes/todo.txt'))
print(os.path.splitext('photo.png'))""",
    example_note="Uses the path module that lives inside the os package.",
    prompt="Use <code>import os.path</code> to write <code>split_name(filename)</code> that returns the result of <code>os.path.splitext(filename)</code>: the name and the extension as a tuple.",
    starter=r"""# import os.path

def split_name(filename):
    # return os.path.splitext(filename)
    pass
""",
    solution=r"""import os.path

def split_name(filename):
    return os.path.splitext(filename)""",
    hints=["Put import os.path at the top of the file.", "os.path.splitext splits at the last dot.", "return os.path.splitext(filename)"],
    tests={"cases": [vis("split_name('report.pdf')", True), vis("split_name('archive.tar.gz')"), vis("split_name('README')")], "requires": ["import", "os.path"]},
)
lesson(
    title="Exception Handling (try, except, finally)", minutes=7,
    concept="An <b>exception</b> is an error that stops your program, like dividing by zero. Wrap risky code in <code>try:</code> and catch the problem with <code>except ZeroDivisionError:</code> so the program carries on. "
            "A <code>finally:</code> block runs at the end whether or not an error happened.",
    why="Real programs must survive bad input, missing files and network failures instead of crashing.",
    example=r"""try:
    print(10 / 0)
except ZeroDivisionError:
    print('Cannot divide by zero')
finally:
    print('Done')""",
    example_note="Catches the error, prints a friendly message, then runs finally.",
    prompt="Write <code>safe_divide(a, b)</code> that returns <code>a / b</code>, but returns the text <code>'Cannot divide by zero'</code> when <code>b</code> is 0. Use <code>try</code> and <code>except</code>.",
    starter=r"""def safe_divide(a, b):
    # try the division, catch ZeroDivisionError
    pass
""",
    solution=r"""def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 'Cannot divide by zero'""",
    hints=["Put the division inside try:", "Catch it with except ZeroDivisionError:", "try: return a / b  /  except ZeroDivisionError: return 'Cannot divide by zero'"],
    tests={"cases": [vis("safe_divide(10, 2)", True), vis("safe_divide(1, 0)"), vis("safe_divide(7, 2)"), vis("safe_divide(0, 5)")], "requires": ["try", "except"]},
)
lesson(
    title="Custom Exceptions (raise)", minutes=8,
    concept="You can signal your own errors with <code>raise</code>. Make a new error type by writing a class that inherits from <code>Exception</code>: <code>class MyError(Exception): pass</code>. "
            "Then <code>raise MyError('message')</code> stops the function, and callers can catch it with <code>except MyError as e</code>; <code>str(e)</code> is the message.",
    why="Custom errors give clear names to problems in your own rules, like <code>InsufficientFunds</code> in a banking app.",
    example=r"""class TooYoung(Exception):
    pass

def check_age(age):
    if age < 18:
        raise TooYoung('Must be 18 or older')
    return 'OK'

try:
    check_age(15)
except TooYoung as e:
    print('Error:', e)""",
    example_note="Raises a custom error and catches it, printing its message.",
    prompt="Create <code>class InsufficientFunds(Exception)</code>. Write <code>withdraw(balance, amount)</code> that raises <code>InsufficientFunds('Not enough money')</code> if <code>amount</code> is more than <code>balance</code>, otherwise returns the new balance. The <code>check</code> helper is already written for you.",
    starter=r"""# 1. define the InsufficientFunds exception class
# 2. define withdraw(balance, amount) that uses raise

def check(balance, amount):
    try:
        return withdraw(balance, amount)
    except InsufficientFunds as e:
        return f'Error: {e}'
""",
    solution=r"""class InsufficientFunds(Exception):
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFunds('Not enough money')
    return balance - amount

def check(balance, amount):
    try:
        return withdraw(balance, amount)
    except InsufficientFunds as e:
        return f'Error: {e}'""",
    hints=["class InsufficientFunds(Exception): with pass inside.", "In withdraw, test amount > balance first.", "raise InsufficientFunds('Not enough money') in that if; otherwise return balance - amount."],
    tests={"cases": [vis("check(100, 30)", True), vis("check(100, 500)"), vis("check(50, 50)"), vis("check(0, 1)")], "requires": ["raise", "class", "Exception"]},
)
lesson(
    title="File Handling (read, write, append)", minutes=8,
    concept="Open a file with <code>with open('name.txt', mode) as f:</code>; the <code>with</code> closes it for you. Modes: <code>'r'</code> read, <code>'w'</code> write (erases old content), <code>'a'</code> append (adds at the end). "
            "Use <code>f.write(text)</code> to write and <code>f.read()</code> to read it all back.",
    why="Saving notes, logs and results to disk lets data live after your program ends.",
    example=r"""with open('hello.txt', 'w') as f:
    f.write('Line one\n')
with open('hello.txt', 'a') as f:
    f.write('Line two\n')
with open('hello.txt') as f:
    print(f.read())""",
    example_note="Writes a file, appends to it, then reads it back.",
    prompt="Write <code>make_notes(first, second)</code>. It writes <code>first</code> and a newline into <code>notes.txt</code> (mode <code>'w'</code>), appends <code>second</code> and a newline (mode <code>'a'</code>), then reads the file and returns its lines as a list (<code>splitlines()</code>).",
    starter=r"""def make_notes(first, second):
    # write first, append second, read back
    pass
""",
    solution=r"""def make_notes(first, second):
    with open('notes.txt', 'w') as f:
        f.write(first + '\n')
    with open('notes.txt', 'a') as f:
        f.write(second + '\n')
    with open('notes.txt') as f:
        return f.read().splitlines()""",
    hints=["Use three with open(...) blocks: write, append, read.", "Write with f.write(first + '\\n') in mode 'w'.", "Return f.read().splitlines() from the last block."],
    tests={"cases": [vis("make_notes('Buy milk', 'Call Ravi')", True), vis("make_notes('a', 'b')"), vis("make_notes('', 'x')")], "requires": ["with open", "write("]},
)
lesson(
    title="JSON Handling", minutes=8,
    concept="<b>JSON</b> is a text format for data that looks like Python dicts and lists. <code>json.dumps(obj)</code> turns an object into a JSON string and <code>json.loads(text)</code> turns it back. "
            "<code>json.dump(obj, file)</code> and <code>json.load(file)</code> do the same with open files.",
    why="Websites, apps and settings files all exchange data as JSON.",
    example=r"""import json

data = {'name': 'Asha', 'age': 20}
text = json.dumps(data)
print(text)
print(json.loads(text)['name'])""",
    example_note="Converts a dict to a JSON string and reads a value back.",
    prompt="Write <code>save_and_load(data)</code>: save <code>data</code> to <code>data.json</code> with <code>json.dump</code>, read it back with <code>json.load</code>, and return <code>json.dumps(loaded, sort_keys=True)</code>.",
    starter=r"""import json

def save_and_load(data):
    # json.dump to a file, json.load it back, return json.dumps(..., sort_keys=True)
    pass
""",
    solution=r"""import json

def save_and_load(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)
    with open('data.json') as f:
        loaded = json.load(f)
    return json.dumps(loaded, sort_keys=True)""",
    hints=["Open data.json with 'w' and call json.dump(data, f).", "Open it again for reading and call json.load(f).", "return json.dumps(loaded, sort_keys=True)"],
    tests={"cases": [vis("save_and_load({'name': 'Asha', 'age': 20})", True), vis("save_and_load([1, 2, 3])"), vis("save_and_load({'ok': True, 'items': [], 'none': None})")], "requires": ["json.dump(", "json.load("]},
)
lesson(
    title="CSV Handling", minutes=8,
    concept="<b>CSV</b> files store tables as text, one row per line with values separated by commas. <code>csv.reader(file)</code> gives each row as a list of strings, and <code>csv.writer(file)</code> writes rows with <code>writerow()</code>. "
            "Any file-like object works, including <code>io.StringIO(text)</code>, a file made from a string.",
    why="Spreadsheets and exported reports are CSV files, so reading them is a common data task.",
    example=r"""import csv
import io

text = 'item,price\npen,10\nbook,45'
for row in csv.reader(io.StringIO(text)):
    print(row)""",
    example_note="Prints each row as a list of strings.",
    prompt="Write <code>total_price(csv_text)</code> that reads CSV text with a header row (<code>item,price</code>) using <code>csv.reader</code> and returns the sum of the prices as an integer.",
    starter=r"""import csv
import io

def total_price(csv_text):
    # reader = csv.reader(io.StringIO(csv_text)); skip the header with next(reader)
    pass
""",
    solution=r"""import csv
import io

def total_price(csv_text):
    reader = csv.reader(io.StringIO(csv_text))
    next(reader)
    total = 0
    for row in reader:
        total += int(row[1])
    return total""",
    hints=["Call next(reader) once to skip the header.", "Each row is a list: row[1] is the price text, so use int().", "Loop over reader, add int(row[1]) to a total and return it."],
    tests={"cases": [vis("total_price('item,price\\npen,10\\nbook,45')", True), vis("total_price('item,price')"), vis("total_price('item,price\\ntea,5')"), vis("total_price('item,price\\na,1\\nb,2\\nc,3\\n')")], "requires": ["csv.reader"]},
)
lesson(
    title="Regular Expressions (re module)", minutes=8,
    concept="A <b>regular expression</b> is a pattern for finding text. With <code>import re</code>, <code>re.findall(pattern, text)</code> returns all matches as a list. "
            "In patterns <code>\\d</code> means a digit, <code>+</code> means one or more, so <code>\\d+</code> matches whole numbers. Write patterns as raw strings: <code>r'\\d+'</code>.",
    why="Validating emails and phone numbers or pulling data out of messy text are classic regex jobs.",
    example=r"""import re

text = 'Order 12 has 3 items'
print(re.findall(r'\d+', text))
print(bool(re.search(r'items', text)))""",
    example_note="Finds the numbers in a sentence, then checks a word is present.",
    prompt="Write <code>extract_numbers(text)</code> that returns a list of all the whole numbers (as strings) found in the text, using <code>re.findall</code>.",
    starter=r"""import re

def extract_numbers(text):
    # return re.findall(r'...', text)
    pass
""",
    solution=r"""import re

def extract_numbers(text):
    return re.findall(r'\d+', text)""",
    hints=["re.findall(pattern, text) returns a list of matches.", "\\d+ matches one or more digits.", "return re.findall(r'\\d+', text)"],
    tests={"cases": [vis("extract_numbers('Order 12 has 3 items costing 450')", True), vis("extract_numbers('no digits here')"), vis("extract_numbers('abc 007 x9')"), vis("extract_numbers('')")], "requires": ["re."]},
)

out = {"title": "Level 5 · Intermediate Python",
       "blurb": "Comprehensions, modules, error handling and working with files, JSON, CSV and regular expressions.",
       "lessons": L}
Path(__file__).with_name("level5.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote level5.json with", len(L), "lessons")
