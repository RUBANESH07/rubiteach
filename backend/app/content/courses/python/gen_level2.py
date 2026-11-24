"""Generates level2.json. Run: python gen_level2.py"""
import json
from pathlib import Path

L = []


def lesson(**kw):
    kw.setdefault("minutes", 5)
    kw.setdefault("xp", 10)
    L.append(kw)


def cases(*stdins):
    out = []
    for i, s in enumerate(stdins):
        c = {"stdin": s}
        if i:
            c["visible"] = False
        out.append(c)
    return out


lesson(
    title="If Statement",
    concept="An <code>if</code> statement runs a block of code only when a condition is <code>True</code>. Write <code>if condition:</code> and indent the lines that belong to it. "
            "If the condition is <code>False</code>, Python simply skips the indented block.",
    why="Programs constantly make choices: show a discount only if the bill is large, or let a user in only if the password matches.",
    example="marks = 72\nif marks >= 40:\n    print('You passed!')\nprint('Done')",
    example_note="Prints 'You passed!' because the condition is true, then always prints 'Done'.",
    prompt="Read a mark as an integer. If it is <code>40</code> or more, print <code>You passed!</code>. After the <code>if</code> block, always print <code>Result checked</code>.",
    starter="marks = int(input())\n# if marks >= 40, print 'You passed!'\n# then print 'Result checked' (outside the if)\n",
    solution="marks = int(input())\nif marks >= 40:\n    print('You passed!')\nprint('Result checked')",
    hints=["Start with: if marks >= 40:", "The line under the if must be indented with 4 spaces.", "Put print('Result checked') back at the left edge, so it always runs."],
    tests={"cases": cases("75\n", "40\n", "12\n"), "requires": ["if"]},
)
lesson(
    title="If Else",
    concept="<code>else</code> gives the other path: it runs when the <code>if</code> condition is <code>False</code>. Exactly one of the two blocks runs. Write <code>else:</code> at the same indentation as <code>if</code>.",
    why="Yes/no decisions are everywhere: can the user vote, is the item in stock, is the payment successful.",
    example="age = 15\nif age >= 18:\n    print('Adult')\nelse:\n    print('Minor')",
    example_note="Prints 'Minor' because 15 is not 18 or more.",
    prompt="Read an age as an integer. If the age is <code>18</code> or more print <code>Eligible to vote</code>, otherwise print <code>Not eligible</code>.",
    starter="age = int(input())\n# use if / else\n",
    solution="age = int(input())\nif age >= 18:\n    print('Eligible to vote')\nelse:\n    print('Not eligible')",
    hints=["You need both an if and an else.", "else: has no condition after it.", "if age >= 18: print('Eligible to vote') / else: print('Not eligible')"],
    tests={"cases": cases("20\n", "18\n", "17\n"), "requires": ["if", "else"]},
)
lesson(
    title="If Elif Else",
    concept="When there are more than two choices, use <code>elif</code> (short for 'else if'). Python checks the conditions from top to bottom and runs the <b>first</b> one that is true; <code>else</code> catches everything left.",
    why="Grades, tax slabs, delivery charges and shipping zones all have several ranges.",
    example="score = 82\nif score >= 90:\n    print('A')\nelif score >= 75:\n    print('B')\nelse:\n    print('C')",
    example_note="82 is not 90 or more, but is 75 or more, so it prints B.",
    prompt="Read marks as an integer and print a grade: <code>A</code> for 90 or more, <code>B</code> for 75 or more, <code>C</code> for 50 or more, otherwise <code>Fail</code>.",
    starter="marks = int(input())\n# use if / elif / else\n",
    solution="marks = int(input())\nif marks >= 90:\n    print('A')\nelif marks >= 75:\n    print('B')\nelif marks >= 50:\n    print('C')\nelse:\n    print('Fail')",
    hints=["Check the highest range first.", "Use elif for the middle ranges.", "if >= 90 -> A, elif >= 75 -> B, elif >= 50 -> C, else -> Fail."],
    tests={"cases": cases("92\n", "80\n", "50\n", "49\n", "90\n"), "requires": ["elif"]},
)
lesson(
    title="Nested If",
    concept="You can put an <code>if</code> inside another <code>if</code>. The inner check only happens when the outer condition is true. Indent the inner block one more level.",
    why="Real checks come in steps: first is the amount valid, and only then is there enough balance.",
    example="logged_in = True\nis_admin = False\nif logged_in:\n    if is_admin:\n        print('Admin panel')\n    else:\n        print('User page')",
    example_note="Checks login first, then the role; prints 'User page'.",
    prompt="Read a <code>balance</code> and then a withdrawal <code>amount</code> (both integers). If the amount is more than 0, then: print <code>Withdrawal successful</code> if it is not more than the balance, otherwise <code>Insufficient balance</code>. If the amount is 0 or less, print <code>Invalid amount</code>.",
    starter="balance = int(input())\namount = int(input())\n# outer if: amount > 0\n#     inner if/else: compare with balance\n# else: Invalid amount\n",
    solution="balance = int(input())\namount = int(input())\nif amount > 0:\n    if amount <= balance:\n        print('Withdrawal successful')\n    else:\n        print('Insufficient balance')\nelse:\n    print('Invalid amount')",
    hints=["First check the amount is valid with an outer if.", "Inside it, write a second if/else comparing amount with balance.", "The final else (Invalid amount) lines up with the outer if."],
    tests={"cases": cases("1000\n500\n", "1000\n1000\n", "1000\n1500\n", "1000\n0\n", "500\n-20\n"), "requires": ["if", "else"]},
)
lesson(
    title="Ternary Operator",
    concept="The <b>ternary operator</b> is a one-line if/else that gives a value: <code>value_if_true if condition else value_if_false</code>. It is handy for picking one of two values to store or print.",
    why="Short choices such as a 'Free' or 'Paid' label, or 'Open' or 'Closed', fit neatly in one line.",
    example="age = 20\nstatus = 'Adult' if age >= 18 else 'Minor'\nprint(status)",
    example_note="Stores 'Adult' in status in a single line.",
    prompt="Read an integer <code>n</code>. Using a one-line ternary expression stored in <code>result</code>, set it to <code>Even</code> or <code>Odd</code>, then print <code>result</code>.",
    starter="n = int(input())\n# result = ... if ... else ...\n# print(result)\n",
    solution="n = int(input())\nresult = 'Even' if n % 2 == 0 else 'Odd'\nprint(result)",
    hints=["The pattern is: A if condition else B.", "n % 2 == 0 is true for even numbers.", "result = 'Even' if n % 2 == 0 else 'Odd'"],
    tests={"cases": cases("4\n", "7\n", "0\n"), "requires": ["result", " if ", " else "], "forbid": ["elif"]},
)
lesson(
    title="For Loop",
    concept="A <code>for</code> loop repeats a block once for every item in a sequence. In <code>for letter in word:</code>, the variable <code>letter</code> takes each character in turn. Indent the lines you want repeated.",
    why="Going through every product in a cart, every student in a class or every line of a file is a for loop.",
    example="for fruit in ['apple', 'mango', 'kiwi']:\n    print(fruit)",
    example_note="Prints each fruit on its own line.",
    prompt="Read a word. Use a <code>for</code> loop to print each letter of the word on its own line.",
    starter="word = input()\n# for letter in word: print it\n",
    solution="word = input()\nfor letter in word:\n    print(letter)",
    hints=["A string is a sequence of letters, so you can loop over it.", "for letter in word:", "Indent print(letter) under the for line."],
    tests={"cases": cases("cat\n", "Python\n", "a\n"), "requires": ["for", "in"]},
)
lesson(
    title="While Loop",
    concept="A <code>while</code> loop repeats as long as its condition stays <code>True</code>. Something inside the loop must change the condition (like <code>n -= 1</code>), otherwise it runs forever.",
    why="Use it when you do not know in advance how many repeats you need: keep asking until the input is valid, or count down a timer.",
    example="n = 3\nwhile n > 0:\n    print(n)\n    n -= 1\nprint('Go!')",
    example_note="Counts 3, 2, 1 then prints Go!.",
    prompt="Read an integer <code>n</code>. Use a <code>while</code> loop to count down from <code>n</code> to <code>1</code>, one number per line, then print <code>Liftoff!</code>.",
    starter="n = int(input())\n# while n > 0: print n, then reduce it\n# finally print 'Liftoff!'\n",
    solution="n = int(input())\nwhile n > 0:\n    print(n)\n    n -= 1\nprint('Liftoff!')",
    hints=["The loop should run while n is greater than 0.", "Do not forget n -= 1 inside the loop.", "Print 'Liftoff!' after the loop, at the left edge."],
    tests={"cases": cases("3\n", "1\n", "0\n"), "requires": ["while", "-="]},
)
lesson(
    title="Nested Loops", minutes=6,
    concept="A loop inside a loop is a <b>nested loop</b>: the inner loop runs completely for every step of the outer loop. <code>range(3)</code> gives <code>0, 1, 2</code> (you will learn it fully in a later lesson). Use <code>print('*', end='')</code> to stay on the same line.",
    why="Tables, grids, seating plans and patterns are built with loops inside loops.",
    example="for row in range(2):\n    for col in range(3):\n        print('*', end='')\n    print()",
    example_note="Prints 2 rows of 3 stars.",
    prompt="Read an integer <code>n</code>. Print a triangle: row 1 has 1 star, row 2 has 2 stars, up to row <code>n</code> with <code>n</code> stars. Use <code>range(1, n + 1)</code> for the rows and a nested loop for the stars.",
    starter="n = int(input())\nfor row in range(1, n + 1):\n    # inner loop: print row stars on one line\n    pass\n",
    solution="n = int(input())\nfor row in range(1, n + 1):\n    for star in range(row):\n        print('*', end='')\n    print()",
    hints=["The inner loop should repeat 'row' times.", "print('*', end='') keeps stars on one line; a plain print() ends the row.", "for star in range(row): print('*', end='') then print() after it."],
    tests={"cases": cases("3\n", "1\n", "4\n"), "requires": ["for", "end="]},
)
lesson(
    title="Break",
    concept="<code>break</code> stops a loop immediately, even if the loop condition is still true. Combined with <code>while True:</code> it gives a loop that runs until something special happens.",
    why="Programs keep reading input until the user types 'quit', or stop searching once an item is found.",
    example="while True:\n    word = input()\n    if word == 'stop':\n        break\n    print(word)",
    example_note="Echoes lines until 'stop' is typed.",
    prompt="Read numbers one per line and add them to a <code>total</code>. When the number <code>0</code> is read, stop the loop with <code>break</code> and print the total.",
    starter="total = 0\nwhile True:\n    n = int(input())\n    # if n is 0: break\n    # otherwise add it to total\n# print total\n",
    solution="total = 0\nwhile True:\n    n = int(input())\n    if n == 0:\n        break\n    total += n\nprint(total)",
    hints=["Check for 0 right after reading the number.", "if n == 0: break", "Add with total += n after the if, and print total after the loop."],
    tests={"cases": cases("5\n10\n0\n", "0\n", "3\n4\n5\n0\n99\n"), "requires": ["while", "break"]},
)
lesson(
    title="Continue",
    concept="<code>continue</code> skips the rest of the current round and jumps to the next one. The loop itself keeps going; only this round is cut short.",
    why="Skipping bad data, such as blank rows or invalid entries, while still processing everything else.",
    example="for n in range(1, 6):\n    if n == 3:\n        continue\n    print(n)",
    example_note="Prints 1 2 4 5 (each on its own line), skipping 3.",
    prompt="Read 5 daily sales amounts (one per line). A negative amount is a wrong entry: skip it with <code>continue</code>. Print the <code>total</code> of the valid amounts.",
    starter="total = 0\nfor day in range(5):\n    amount = int(input())\n    # if amount is negative: continue\n    # add amount to total\n# print total\n",
    solution="total = 0\nfor day in range(5):\n    amount = int(input())\n    if amount < 0:\n        continue\n    total += amount\nprint(total)",
    hints=["Test amount < 0 before adding.", "if amount < 0: continue", "total += amount comes after the if; print(total) after the loop."],
    tests={"cases": cases("100\n200\n-50\n300\n50\n", "10\n20\n30\n40\n50\n", "-1\n-2\n-3\n-4\n-5\n"), "requires": ["continue"]},
)
lesson(
    title="Pass",
    concept="<code>pass</code> is a statement that does nothing. Python needs at least one line inside every block, so <code>pass</code> is a placeholder when you have not written the code yet.",
    why="Developers sketch the structure of a program first and use <code>pass</code> to fill in the blanks later.",
    example="mark = 80\nif mark >= 40:\n    pass  # TODO: add congratulations later\nelse:\n    print('Try again')",
    example_note="Prints nothing, because the passing branch is an empty placeholder.",
    prompt="Read a mark as an integer. If it is <code>40</code> or more, leave the block as just <code>pass</code> (placeholder). Otherwise print <code>Needs improvement</code>. Finally print <code>Checked</code>.",
    starter="mark = int(input())\n# if mark >= 40: use pass\n# else: print 'Needs improvement'\n# always print 'Checked'\n",
    solution="mark = int(input())\nif mark >= 40:\n    pass\nelse:\n    print('Needs improvement')\nprint('Checked')",
    hints=["An empty if block is an error, so write pass in it.", "The else branch prints the message.", "print('Checked') goes at the left edge at the end."],
    tests={"cases": cases("80\n", "20\n", "40\n"), "requires": ["pass", "else"]},
)
lesson(
    title="Range",
    concept="<code>range(start, stop, step)</code> makes a sequence of numbers. It <b>stops before</b> <code>stop</code>. <code>range(5)</code> is 0-4, <code>range(1, 6)</code> is 1-5 and <code>range(2, 11, 2)</code> is 2, 4, 6, 8, 10.",
    why="Whenever you need to repeat something a set number of times, or count by 2s, 5s or 10s, you use range.",
    example="for i in range(1, 10, 3):\n    print(i)",
    example_note="Prints 1, 4 and 7.",
    prompt="Read an integer <code>n</code>. Use a <code>for</code> loop with <code>range</code> (with a step of 2) to print all even numbers from <code>2</code> up to <code>n</code>, one per line. Then print <code>Done</code>.",
    starter="n = int(input())\n# for i in range(2, ?, 2): print(i)\n# then print 'Done'\n",
    solution="n = int(input())\nfor i in range(2, n + 1, 2):\n    print(i)\nprint('Done')",
    hints=["Start at 2 and step by 2.", "The stop value is excluded, so use n + 1.", "for i in range(2, n + 1, 2):"],
    tests={"cases": cases("10\n", "7\n", "1\n"), "requires": ["range("]},
)
lesson(
    title="Loop Else", minutes=6,
    concept="A loop can have an <code>else</code> block. It runs when the loop finishes <b>without</b> hitting <code>break</code>. If <code>break</code> happens, the <code>else</code> is skipped.",
    why="It is a neat way to do 'search the list; if not found, say so' without extra flag variables.",
    example="for n in [1, 3, 5]:\n    if n % 2 == 0:\n        print('Found even')\n        break\nelse:\n    print('No even number')",
    example_note="No even number is found, so the loop's else prints the message.",
    prompt="The roll numbers present today are <code>[101, 102, 103, 104]</code>. Read a roll number. Loop through the list: if it matches, print <code>Present</code> and <code>break</code>. Use a loop <code>else</code> to print <code>Absent</code> when no match was found.",
    starter="present = [101, 102, 103, 104]\nroll = int(input())\n# for r in present: if r == roll -> print 'Present' and break\n# else: print 'Absent'\n",
    solution="present = [101, 102, 103, 104]\nroll = int(input())\nfor r in present:\n    if r == roll:\n        print('Present')\n        break\nelse:\n    print('Absent')",
    hints=["The else lines up with for, not with if.", "break skips the loop's else.", "for r in present: if r == roll: print('Present'); break  /  else: print('Absent')"],
    tests={"cases": cases("103\n", "105\n", "101\n", "104\n"), "requires": ["for", "break", "else:"]},
)

out = {"title": "Level 2 · Conditional Statements and Loops",
       "blurb": "Make decisions with if statements and repeat work with for and while loops.",
       "lessons": L}
Path(__file__).with_name("level2.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote level2.json with", len(L), "lessons")
