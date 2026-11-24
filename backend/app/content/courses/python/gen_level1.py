"""Generates level1.json. Run: python gen_level1.py   (kept as the authoring source and as a model for other levels)"""
import json
from pathlib import Path

L = []


def lesson(**kw):
    kw.setdefault("minutes", 5)
    kw.setdefault("xp", 10)
    L.append(kw)


lesson(
    title="Introduction: syntax, indentation, comments", minutes=6,
    concept="Python programs are lists of instructions run top to bottom. <code>print()</code> shows text on the screen. "
            "Python uses <b>indentation</b> (spaces at the start of a line) to group code, and a <code>#</code> starts a <b>comment</b>: a note for humans that Python ignores.",
    why="Readable, simple syntax is why Python is used to build websites, analyse data and automate boring work.",
    example="# This line is a comment\nprint('Welcome to Rubitech Academy')\nprint('Learning Python is fun')",
    example_note="Prints two lines; the comment is ignored.",
    prompt="Write a program that prints exactly <code>Hello, Python!</code> on one line.",
    starter="# Write your code below\n",
    solution="print('Hello, Python!')",
    hints=["Use the print() function.", "Text goes inside quotes: print('...').", "print('Hello, Python!')"],
    tests={"cases": [{}], "requires": ["print"]},
)
lesson(
    title="Variables",
    concept="A <b>variable</b> is a named box that stores a value. Create one with <code>=</code>, like <code>age = 20</code>. "
            "Names use letters, digits and underscores, cannot start with a digit, and are case-sensitive (<code>Age</code> and <code>age</code> are different).",
    why="Programs constantly remember things: a user's name, a score, a price. Variables are how they remember.",
    example="name = 'Asha'\nage = 21\nprint(name)\nprint(age)",
    example_note="Stores two values in variables and prints them.",
    prompt="Create a variable <code>city</code> that holds <code>'Chennai'</code> and a variable <code>year</code> that holds <code>2026</code>. Then print <code>city</code> on one line and <code>year</code> on the next.",
    starter="# Create the variables, then print them\n",
    solution="city = 'Chennai'\nyear = 2026\nprint(city)\nprint(year)",
    hints=["Create each variable with = on its own line.", "Then call print(city) and print(year).", "city = 'Chennai'  /  year = 2026  /  then print both."],
    tests={"cases": [{}], "requires": ["city", "year"]},
)
lesson(
    title="Data types", minutes=6,
    concept="Every value has a <b>type</b>: <code>int</code> (whole numbers), <code>float</code> (decimals), <code>str</code> (text), <code>bool</code> (<code>True</code>/<code>False</code>), "
            "<code>complex</code> (like <code>3+4j</code>) and <code>None</code> (nothing). Use <code>type(x)</code> to check.",
    why="Python behaves differently for each type: <code>2 + 3</code> adds numbers but <code>'2' + '3'</code> joins text.",
    example="print(type(10))\nprint(type(3.14))\nprint(type('hi'))\nprint(type(True))\nprint(type(None))",
    example_note="Prints the class of five different values.",
    prompt="Print the type of each value on its own line, in this order: <code>42</code>, <code>2.5</code>, <code>'Python'</code>, <code>True</code>, <code>3+4j</code>, <code>None</code>.",
    starter="print(type(42))\n# add the rest\n",
    solution="print(type(42))\nprint(type(2.5))\nprint(type('Python'))\nprint(type(True))\nprint(type(3+4j))\nprint(type(None))",
    hints=["Use print(type(value)) for each one.", "Complex numbers are written like 3+4j.", "Six print(type(...)) lines in the order given."],
    tests={"cases": [{}], "requires": ["type("]},
)
lesson(
    title="Type casting",
    concept="<b>Type casting</b> converts a value to another type: <code>int('7')</code> gives <code>7</code>, <code>float(3)</code> gives <code>3.0</code>, <code>str(99)</code> gives <code>'99'</code>, "
            "and <code>bool(0)</code> is <code>False</code> (only 0, empty text and <code>None</code> are false).",
    why="Data from users and files arrives as text. You must convert it before doing maths.",
    example="price_text = '250'\nprice = int(price_text)\nprint(price + 50)\nprint(bool(0), bool('hello'))",
    example_note="Converts text to a number and shows truthiness.",
    prompt="The variable <code>marks</code> holds the text <code>'87'</code>. Convert it to an integer, add <code>5</code> bonus marks and print the total.",
    starter="marks = '87'\n# convert, add 5, print\n",
    solution="marks = '87'\nprint(int(marks) + 5)",
    hints=["marks is text, so + 5 would fail until you convert it.", "int(marks) turns it into a number.", "print(int(marks) + 5)"],
    tests={"cases": [{}], "requires": ["int("]},
)
lesson(
    title="Operators (arithmetic, comparison, logical)", minutes=7,
    concept="Arithmetic: <code>+ - * / // % **</code> (<code>//</code> whole-number division, <code>%</code> remainder, <code>**</code> power). "
            "Comparison (<code>== != &lt; &gt; &lt;= &gt;=</code>) gives <code>True</code>/<code>False</code>. Logical: <code>and</code>, <code>or</code>, <code>not</code> combine conditions.",
    why="Calculating totals, checking limits and combining rules are in almost every program.",
    example="print(17 // 5, 17 % 5, 2 ** 10)\nprint(7 > 3 and 4 == 4)",
    example_note="Shows division, remainder, power and a combined condition.",
    prompt="Given <code>a = 17</code> and <code>b = 5</code>, print on separate lines: <code>a // b</code>, <code>a % b</code>, <code>a ** 2</code>, and whether <code>a &gt; b and b &gt; 10</code>.",
    starter="a = 17\nb = 5\n# print the four results\n",
    solution="a = 17\nb = 5\nprint(a // b)\nprint(a % b)\nprint(a ** 2)\nprint(a > b and b > 10)",
    hints=["Use four print() calls.", "// is whole-number division and % is the remainder.", "The last one prints False because b > 10 is False."],
    tests={"cases": [{}], "requires": ["//", "%", "**", "and"]},
)
lesson(
    title="Assignment operators",
    concept="Shortcuts update a variable using its own value: <code>x += 3</code> means <code>x = x + 3</code>. The same works for <code>-=</code>, <code>*=</code>, <code>/=</code>, <code>//=</code>, <code>%=</code> and <code>**=</code>.",
    why="Counters, running totals and score updates all use these shortcuts.",
    example="score = 10\nscore += 5\nscore *= 2\nprint(score)",
    example_note="Adds 5 then doubles the score, printing 30.",
    prompt="Start with <code>balance = 1000</code>. Use assignment operators to add <code>250</code>, then subtract <code>100</code>, then multiply by <code>2</code>. Print the final <code>balance</code>.",
    starter="balance = 1000\n# update balance with +=, -=, *=\n",
    solution="balance = 1000\nbalance += 250\nbalance -= 100\nbalance *= 2\nprint(balance)",
    hints=["Use one assignment operator per line.", "balance += 250 first.", "balance += 250, balance -= 100, balance *= 2, then print(balance)."],
    tests={"cases": [{}], "requires": ["+=", "-=", "*="]},
)
lesson(
    title="Membership operators",
    concept="<code>in</code> checks whether a value is inside a collection or text, and <code>not in</code> checks that it is not. Both return <code>True</code> or <code>False</code>.",
    why="Checking if a username is taken or a letter appears in a word is a membership test.",
    example="fruits = ['apple', 'banana']\nprint('apple' in fruits)\nprint('p' in 'python')\nprint('z' not in 'python')",
    example_note="Tests membership in a list and in text.",
    prompt="Given <code>word = 'academy'</code> and <code>vowels = 'aeiou'</code>, print whether <code>'a'</code> is in <code>word</code>, whether <code>'z'</code> is in <code>word</code>, and whether <code>'x'</code> is <b>not</b> in <code>vowels</code> (three lines).",
    starter="word = 'academy'\nvowels = 'aeiou'\n# three print() lines\n",
    solution="word = 'academy'\nvowels = 'aeiou'\nprint('a' in word)\nprint('z' in word)\nprint('x' not in vowels)",
    hints=["Use in and not in inside print().", "print('a' in word) prints True.", "The last line is print('x' not in vowels)."],
    tests={"cases": [{}], "requires": ["in ", "not in"]},
)
lesson(
    title="Identity operators",
    concept="<code>is</code> checks whether two names point to the <b>same object</b> in memory; <code>==</code> checks whether the values are <b>equal</b>. Two equal lists are different objects, so <code>is</code> is <code>False</code>. Use <code>is None</code> to test for nothing.",
    why="Mixing up <code>is</code> and <code>==</code> causes subtle bugs, and <code>is None</code> is the standard way to check for missing values.",
    example="a = [1, 2]\nb = [1, 2]\nc = a\nprint(a == b, a is b, a is c)",
    example_note="Equal values, but only c is the same object as a.",
    prompt="With <code>x = [1, 2, 3]</code>, <code>y = [1, 2, 3]</code> and <code>z = x</code>, print on separate lines: <code>x == y</code>, <code>x is y</code>, <code>x is z</code>, and <code>x is not y</code>.",
    starter="x = [1, 2, 3]\ny = [1, 2, 3]\nz = x\n# four print() lines\n",
    solution="x = [1, 2, 3]\ny = [1, 2, 3]\nz = x\nprint(x == y)\nprint(x is y)\nprint(x is z)\nprint(x is not y)",
    hints=["== compares values, is compares identity.", "z = x makes z the very same list as x.", "Expected output: True, False, True, True."],
    tests={"cases": [{}], "requires": [" is ", "is not"]},
)
lesson(
    title="Bitwise operators", minutes=7,
    concept="Bitwise operators work on the binary digits of integers: <code>&amp;</code> (AND), <code>|</code> (OR), <code>^</code> (XOR), <code>~</code> (NOT), <code>&lt;&lt;</code> and <code>&gt;&gt;</code> (shift). "
            "For example <code>5 &amp; 3</code> is <code>1</code> because <code>101</code> and <code>011</code> share only the last bit.",
    why="Bitwise tricks power permissions flags, graphics, networking and fast maths.",
    example="print(5 & 3, 5 | 3, 5 ^ 3)\nprint(1 << 4)",
    example_note="AND, OR, XOR of 5 and 3, and shifting 1 left four places.",
    prompt="With <code>a = 12</code> and <code>b = 10</code>, print on separate lines: <code>a &amp; b</code>, <code>a | b</code>, <code>a ^ b</code>, <code>a &lt;&lt; 2</code> and <code>a &gt;&gt; 1</code>.",
    starter="a = 12\nb = 10\n# five print() lines\n",
    solution="a = 12\nb = 10\nprint(a & b)\nprint(a | b)\nprint(a ^ b)\nprint(a << 2)\nprint(a >> 1)",
    hints=["12 is 1100 and 10 is 1010 in binary.", "Each operator goes in its own print().", "Expected output: 8, 14, 6, 48, 6."],
    tests={"cases": [{}], "requires": ["&", "|", "^", "<<", ">>"]},
)
lesson(
    title="Input / Output and f-strings", minutes=7,
    concept="<code>input()</code> reads a line the user types (always as text). <code>print()</code> shows output. An <b>f-string</b> puts values inside text: <code>f'Hello {name}'</code>; you can format numbers like <code>{price:.2f}</code> for 2 decimals.",
    why="Every interactive program reads input and shows friendly output.",
    example="name = 'Asha'\nmarks = 91.456\nprint(f'{name} scored {marks:.1f}')",
    example_note="Builds one sentence from two variables with one decimal place.",
    prompt="Read a name and an age (two separate lines of input). Print <code>Hello, NAME! Next year you will be AGE+1.</code> using an f-string. Example: input <code>Ravi</code> and <code>20</code> prints <code>Hello, Ravi! Next year you will be 21.</code>",
    starter="name = input()\nage = input()\n# print the greeting using an f-string\n",
    solution="name = input()\nage = int(input())\nprint(f'Hello, {name}! Next year you will be {age + 1}.')",
    hints=["input() gives text, so convert the age with int().", "Inside an f-string you can write {age + 1}.", "print(f'Hello, {name}! Next year you will be {age + 1}.')"],
    tests={"cases": [{"stdin": "Ravi\n20\n"}, {"stdin": "Mei\n35\n", "visible": False}, {"stdin": "Sam\n0\n", "visible": False}], "requires": ["f'"]},
)

out = {"title": "Level 1 · Python Basics",
       "blurb": "Syntax, variables, types, operators and your first input and output.",
       "lessons": L}
Path(__file__).with_name("level1.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote level1.json with", len(L), "lessons")
