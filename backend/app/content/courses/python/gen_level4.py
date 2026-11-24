"""Generates level4.json. Run: python gen_level4.py"""
import json
from pathlib import Path

L = []


def lesson(**kw):
    kw.setdefault("minutes", 5)
    kw.setdefault("xp", 15)
    L.append(kw)


def vis(expr, visible=False):
    return {"expr": expr, "visible": visible}


lesson(
    title="Functions (def, calling)",
    concept="A <b>function</b> is a named block of code you write once and run whenever you need it. Create one with <code>def</code>, a name, brackets and a colon; the indented lines below are its body. "
            "Nothing runs until you <b>call</b> the function by writing its name with brackets, like <code>greet()</code>.",
    why="Functions stop you repeating code: a shop app has one <code>print_bill()</code> that every checkout uses.",
    example=r"""def welcome(name):
    print('Welcome,', name)

welcome('Asha')
welcome('Ravi')""",
    example_note="Defines a function once and calls it twice with different names.",
    prompt="Define a function <code>greet(name)</code> that prints <code>Hello, NAME!</code>. Then read a name from input and call <code>greet</code> with it. Example: <code>Asha</code> prints <code>Hello, Asha!</code>",
    starter=r"""def greet(name):
    # print the greeting here
    pass

name = input()
# call greet with name
""",
    solution=r"""def greet(name):
    print(f'Hello, {name}!')

name = input()
greet(name)""",
    hints=["Inside the function use print().", "An f-string helps: f'Hello, {name}!'", "After the def, write greet(name) on its own line."],
    tests={"cases": [{"stdin": "Asha\n"}, {"stdin": "Ravi Kumar\n", "visible": False}, {"stdin": "Z\n", "visible": False}], "requires": ["def "]},
)
lesson(
    title="Parameters (positional and keyword)",
    concept="<b>Parameters</b> are the names in the brackets of a <code>def</code>; the values you pass are <b>arguments</b>. "
            "<b>Positional</b> arguments match by order: <code>bill(50, 3)</code>. <b>Keyword</b> arguments match by name, so order does not matter: <code>bill(quantity=3, price=50)</code>.",
    why="Keyword arguments make calls readable, like <code>send_email(to='a@b.com', subject='Hi')</code>.",
    example=r"""def intro(name, city):
    return name + ' lives in ' + city

print(intro('Asha', 'Pune'))
print(intro(city='Delhi', name='Ravi'))""",
    example_note="Calls the same function by position and by keyword.",
    prompt="Write a function <code>bill(price, quantity)</code> that returns the total cost (<code>price * quantity</code>). The tests call it both by position and by keyword.",
    starter=r"""def bill(price, quantity):
    # return the total
    pass
""",
    solution=r"""def bill(price, quantity):
    return price * quantity""",
    hints=["The function must return a value, not print it.", "Multiply the two parameters.", "return price * quantity"],
    tests={"cases": [vis("bill(50, 3)", True), vis("bill(quantity=2, price=10)"), vis("bill(0, 5)"), vis("bill(price=12.5, quantity=4)")], "requires": ["def "]},
)
lesson(
    title="Default Arguments",
    concept="Give a parameter a <b>default value</b> with <code>=</code> in the <code>def</code>: <code>def f(x, rate=0.1)</code>. If the caller leaves that argument out, the default is used; if they pass one, it replaces the default. "
            "Parameters with defaults go after those without.",
    why="Defaults keep common calls short: <code>open('file.txt')</code> works without telling Python the mode.",
    example=r"""def hello(name, greeting='Hello'):
    print(greeting, name)

hello('Asha')
hello('Ravi', 'Namaste')""",
    example_note="Uses the default greeting once and overrides it once.",
    prompt="Write <code>price_with_tax(price, rate=0.18)</code> that returns the price plus tax, rounded to 2 decimals: <code>round(price * (1 + rate), 2)</code>.",
    starter=r"""def price_with_tax(price, rate=0.18):
    # return price plus tax, rounded to 2 decimals
    pass
""",
    solution=r"""def price_with_tax(price, rate=0.18):
    return round(price * (1 + rate), 2)""",
    hints=["The default rate is already in the def line.", "Use round(value, 2).", "return round(price * (1 + rate), 2)"],
    tests={"cases": [vis("price_with_tax(100)", True), vis("price_with_tax(200, 0.05)"), vis("price_with_tax(0)"), vis("price_with_tax(99.99, rate=0)")], "requires": ["def ", "rate=0.18"]},
)
lesson(
    title="Return",
    concept="<code>return</code> sends a value back to whoever called the function and ends it immediately. Without <code>return</code> a function gives back <code>None</code>. "
            "You can return several values separated by commas; Python packs them into a <b>tuple</b>.",
    why="Returned values can be stored, compared or passed to other functions, which printing alone cannot do.",
    example=r"""def add(a, b):
    return a + b

result = add(2, 3)
print(result * 10)""",
    example_note="Stores the returned value and uses it in more maths.",
    prompt="Write <code>min_max(numbers)</code> that returns the smallest and the largest number from a list as two values (a tuple).",
    starter=r"""def min_max(numbers):
    # return the smallest and largest values
    pass
""",
    solution=r"""def min_max(numbers):
    return min(numbers), max(numbers)""",
    hints=["Python has built-in min() and max().", "Return two values separated by a comma.", "return min(numbers), max(numbers)"],
    tests={"cases": [vis("min_max([4, 9, 1])", True), vis("min_max([7])"), vis("min_max([-5, 0, 5, 10])")], "requires": ["return"]},
)
lesson(
    title="*args",
    concept="Put <code>*args</code> in a <code>def</code> to accept <b>any number</b> of positional arguments. Inside the function <code>args</code> is a tuple holding everything passed, so you can loop over it or use <code>sum(args)</code>. "
            "The name <code>args</code> is just a habit; the star is what matters.",
    why="Functions like <code>print()</code> accept as many values as you like; <code>*args</code> is how you build that.",
    example=r"""def show_all(*args):
    print(len(args), 'items:', args)

show_all('a')
show_all(1, 2, 3)""",
    example_note="The same function handles one argument or three.",
    prompt="Write <code>total(*args)</code> that returns the sum of all numbers passed in. With no arguments it returns <code>0</code>.",
    starter=r"""def total(*args):
    # return the sum of args
    pass
""",
    solution=r"""def total(*args):
    return sum(args)""",
    hints=["args is a tuple of all the numbers.", "sum() adds up a tuple.", "return sum(args)"],
    tests={"cases": [vis("total(1, 2, 3)", True), vis("total()"), vis("total(5)"), vis("total(10, 20.5, 30)")], "requires": ["*args"]},
)
lesson(
    title="**kwargs",
    concept="Put <code>**kwargs</code> in a <code>def</code> to accept any number of <b>keyword</b> arguments. Inside the function <code>kwargs</code> is a dictionary: names are keys, values are values. "
            "Loop with <code>kwargs.items()</code>.",
    why="Settings, form fields and options are often passed as named extras, e.g. <code>create_user(name='Asha', age=20)</code>.",
    example=r"""def show(**kwargs):
    for key, value in kwargs.items():
        print(key, '=', value)

show(name='Asha', age=20)""",
    example_note="Prints every keyword argument passed in.",
    prompt="Write <code>describe(**kwargs)</code> that returns the pairs as <code>key=value</code> text joined by <code>', '</code>, sorted by key. <code>describe(name='Asha', age=20)</code> returns <code>'age=20, name=Asha'</code>.",
    starter=r"""def describe(**kwargs):
    # build 'key=value' pieces sorted by key and join them
    pass
""",
    solution=r"""def describe(**kwargs):
    parts = [f'{key}={kwargs[key]}' for key in sorted(kwargs)]
    return ', '.join(parts)""",
    hints=["sorted(kwargs) gives the keys in order.", "Build a list of 'key=value' strings, then use ', '.join(list).", "parts = [f'{k}={kwargs[k]}' for k in sorted(kwargs)]; return ', '.join(parts)"],
    tests={"cases": [vis("describe(name='Asha', age=20)", True), vis("describe()"), vis("describe(city='Pune')"), vis("describe(b=2, a=1, c=3)")], "requires": ["**kwargs"]},
)
lesson(
    title="Lambda",
    concept="A <b>lambda</b> is a tiny nameless function written on one line: <code>lambda x: x * 2</code>. The part before the colon is the parameters, the part after is the value it returns (no <code>return</code> word). "
            "You can store it in a variable and call it like any function.",
    why="Lambdas are handy for quick one-off rules, such as telling <code>sorted()</code> how to order items.",
    example=r"""double = lambda x: x * 2
add = lambda a, b: a + b
print(double(7))
print(add(3, 4))""",
    example_note="Two lambdas stored in variables and called.",
    prompt="Create a lambda stored in <code>add_gst</code> that takes a <code>price</code> and returns it plus 18% GST, rounded to 2 decimals.",
    starter=r"""# add_gst = lambda price: ...
add_gst = None
""",
    solution=r"""add_gst = lambda price: round(price * 1.18, 2)""",
    hints=["Write lambda price: followed by the calculation.", "price * 1.18 adds 18%.", "add_gst = lambda price: round(price * 1.18, 2)"],
    tests={"cases": [vis("add_gst(100)", True), vis("add_gst(0)"), vis("add_gst(250.5)")], "requires": ["lambda"]},
)
lesson(
    title="Recursion", minutes=7,
    concept="A <b>recursive</b> function calls itself on a smaller problem. It needs a <b>base case</b> that stops the calls, otherwise it never ends. "
            "For example <code>5! = 5 * 4!</code> and <code>0! = 1</code> is the base case.",
    why="Recursion fits naturally with nested things: folders inside folders, menus inside menus, family trees.",
    example=r"""def countdown(n):
    if n == 0:
        print('Go!')
        return
    print(n)
    countdown(n - 1)

countdown(3)""",
    example_note="Prints 3, 2, 1 then Go! by calling itself with n - 1.",
    prompt="Write <code>factorial(n)</code> using recursion (no loops). <code>factorial(5)</code> is <code>120</code> and <code>factorial(0)</code> is <code>1</code>.",
    starter=r"""def factorial(n):
    # base case first, then call factorial(n - 1)
    pass
""",
    solution=r"""def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)""",
    hints=["Base case: if n is 0 or 1, return 1.", "Otherwise return n times the factorial of n - 1.", "return n * factorial(n - 1)"],
    tests={"cases": [vis("factorial(5)", True), vis("factorial(0)"), vis("factorial(1)"), vis("factorial(10)")], "requires": ["factorial("], "forbid": ["for ", "while", "math"]},
)
lesson(
    title="Scope (local, global, nonlocal)", minutes=7,
    concept="A variable made inside a function is <b>local</b>: it exists only there. A variable made outside is <b>global</b> and can be read anywhere, but to <i>change</i> it inside a function you must write <code>global name</code> first. "
            "<code>nonlocal</code> does the same for a variable of an enclosing function.",
    why="Understanding scope explains why a variable 'disappears' or why a function cannot update your counter.",
    example=r"""count = 0

def add_one():
    global count
    count += 1

add_one()
add_one()
print(count)""",
    example_note="Without 'global', the function could not change count; this prints 2.",
    prompt="The global <code>total</code> starts at 0. Write <code>add_to_total(amount)</code> that adds <code>amount</code> to the global <code>total</code> and returns the new total.",
    starter=r"""total = 0

def add_to_total(amount):
    # use global, add amount, return the new total
    pass
""",
    solution=r"""total = 0

def add_to_total(amount):
    global total
    total += amount
    return total""",
    hints=["Start the function body with: global total", "Then total += amount.", "global total / total += amount / return total"],
    tests={"cases": [vis("[add_to_total(5), add_to_total(10)]", True), vis("[add_to_total(0)]"), vis("[add_to_total(3), add_to_total(4), add_to_total(5)]")], "requires": ["global"]},
)
lesson(
    title="Nested Functions", minutes=7,
    concept="You can define a function <b>inside</b> another one. The inner function can use the outer function's variables, and if the outer function returns the inner one, it still remembers those variables (a <b>closure</b>). "
            "Use <code>nonlocal</code> in the inner function to change an outer variable.",
    why="Closures let you build custom tools, like a counter or a 'discount maker', each with its own private memory.",
    example=r"""def make_multiplier(n):
    def multiply(x):
        return x * n
    return multiply

triple = make_multiplier(3)
print(triple(5))""",
    example_note="The inner function remembers n = 3 and prints 15.",
    prompt="Write <code>make_counter()</code> that returns a function. Each time that function is called it returns the next number: <code>1</code>, then <code>2</code>, then <code>3</code>... Use an inner function and <code>nonlocal</code>.",
    starter=r"""def make_counter():
    count = 0
    # define an inner function that uses nonlocal, then return it
""",
    solution=r"""def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter""",
    hints=["Define def counter(): inside make_counter.", "Inside counter write nonlocal count, then add 1 and return it.", "Finish with return counter (no brackets) in make_counter."],
    tests={"cases": [vis("(lambda c: [c(), c(), c()])(make_counter())", True), vis("(lambda c: [c()])(make_counter())"), vis("(lambda a, b: [a(), a(), b()])(make_counter(), make_counter())")], "requires": ["nonlocal"]},
)
lesson(
    title="Higher-Order Functions",
    concept="In Python a function is a value, so you can pass it to another function or return it. A <b>higher-order function</b> is one that takes a function as an argument (or returns one). "
            "Pass the function's name <i>without</i> brackets: <code>apply(double, 5)</code>.",
    why="Sorting, filtering and event handlers all work by handing a function to other code.",
    example=r"""def apply(func, value):
    return func(value)

print(apply(len, 'python'))
print(apply(abs, -9))""",
    example_note="The same apply works with any function you give it.",
    prompt="Write <code>apply_twice(func, value)</code> that calls <code>func</code> on <code>value</code>, then calls <code>func</code> again on that result, and returns it.",
    starter=r"""def apply_twice(func, value):
    # call func two times
    pass
""",
    solution=r"""def apply_twice(func, value):
    return func(func(value))""",
    hints=["func is a function you can call: func(value).", "The second call uses the first result.", "return func(func(value))"],
    tests={"cases": [vis("apply_twice(lambda x: x + 3, 10)", True), vis("apply_twice(str.upper, 'ab')"), vis("apply_twice(lambda s: s + '!', 'hi')"), vis("apply_twice(abs, -4)")], "requires": ["func("]},
)
lesson(
    title="Map (map())",
    concept="<code>map(function, items)</code> applies a function to every item and gives back the results. It returns a lazy <b>map object</b>, so wrap it in <code>list()</code> to see the values: <code>list(map(len, ['a', 'bb']))</code> is <code>[1, 2]</code>.",
    why="Converting a whole column of data (prices to rupees, text to numbers) is a classic map job.",
    example=r"""names = ['asha', 'ravi']
print(list(map(str.upper, names)))
print(list(map(lambda x: x * 2, [1, 2, 3])))""",
    example_note="Upper-cases every name and doubles every number.",
    prompt="Write <code>to_fahrenheit(celsius_list)</code> that uses <code>map()</code> to convert each Celsius value with <code>c * 9 / 5 + 32</code>, rounded to 1 decimal, and returns a list.",
    starter=r"""def to_fahrenheit(celsius_list):
    # use map() with a lambda, wrap in list()
    pass
""",
    solution=r"""def to_fahrenheit(celsius_list):
    return list(map(lambda c: round(c * 9 / 5 + 32, 1), celsius_list))""",
    hints=["map(function, celsius_list) needs a function; a lambda works.", "Wrap the map in list().", "list(map(lambda c: round(c * 9 / 5 + 32, 1), celsius_list))"],
    tests={"cases": [vis("to_fahrenheit([0, 100, 37])", True), vis("to_fahrenheit([])"), vis("to_fahrenheit([-40])")], "requires": ["map("]},
)
lesson(
    title="Filter (filter())",
    concept="<code>filter(function, items)</code> keeps only the items for which the function returns <code>True</code>. Like <code>map</code> it is lazy, so wrap it in <code>list()</code>: <code>list(filter(lambda n: n &gt; 2, [1, 5, 3]))</code> is <code>[5, 3]</code>.",
    why="Picking out passing students, in-stock products or valid emails is a filter job.",
    example=r"""nums = [1, 2, 3, 4, 5, 6]
print(list(filter(lambda n: n % 2 == 0, nums)))""",
    example_note="Keeps only the even numbers.",
    prompt="Write <code>passed(marks)</code> that uses <code>filter()</code> to return a list of the marks that are <code>40</code> or more.",
    starter=r"""def passed(marks):
    # use filter() with a lambda, wrap in list()
    pass
""",
    solution=r"""def passed(marks):
    return list(filter(lambda m: m >= 40, marks))""",
    hints=["The lambda must return True for marks you want to keep.", "lambda m: m >= 40", "list(filter(lambda m: m >= 40, marks))"],
    tests={"cases": [vis("passed([35, 80, 40, 12, 99])", True), vis("passed([])"), vis("passed([10, 20])"), vis("passed([40])")], "requires": ["filter("]},
)
lesson(
    title="Reduce (functools.reduce())", minutes=6,
    concept="<code>reduce(function, items, start)</code> from the <code>functools</code> module combines a list into <b>one</b> value. The function takes the running result and the next item. "
            "For example <code>reduce(lambda a, b: a + b, [1, 2, 3], 0)</code> gives <code>6</code>. The third argument is the starting value.",
    why="Totals, products and 'longest word' style summaries are all reductions of a list into a single answer.",
    example=r"""from functools import reduce

nums = [1, 2, 3, 4]
print(reduce(lambda a, b: a + b, nums, 0))""",
    example_note="Adds the numbers step by step and prints 10.",
    prompt="Write <code>product(numbers)</code> that uses <code>reduce</code> to multiply all the numbers together. An empty list gives <code>1</code>.",
    starter=r"""from functools import reduce

def product(numbers):
    # reduce with a lambda and a start value of 1
    pass
""",
    solution=r"""from functools import reduce

def product(numbers):
    return reduce(lambda a, b: a * b, numbers, 1)""",
    hints=["The lambda takes two values: lambda a, b: ...", "Start from 1 so an empty list works.", "reduce(lambda a, b: a * b, numbers, 1)"],
    tests={"cases": [vis("product([2, 3, 4])", True), vis("product([])"), vis("product([7])"), vis("product([5, 0, 9])")], "requires": ["reduce("]},
)

out = {"title": "Level 4 · Functions",
       "blurb": "Write reusable functions: parameters, return values, lambdas, recursion, scope and the map, filter and reduce tools.",
       "lessons": L}
Path(__file__).with_name("level4.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote level4.json with", len(L), "lessons")
