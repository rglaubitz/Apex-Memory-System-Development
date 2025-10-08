# Python Standards & Best Practices

**Research Phase:** Python Standards Collection
**Created:** 2025-10-06
**Quality Tier:** Tier 1 (Official PEPs & Python.org)

---

## Table of Contents

1. [Type Hints Standards (PEP 484)](#type-hints-standards-pep-484)
2. [Async/Await Standards (PEP 492)](#asyncawait-standards-pep-492)
3. [Python Enhancement Proposals (PEPs)](#python-enhancement-proposals-peps)
4. [Best Practices](#best-practices)

---

## Type Hints Standards (PEP 484)

**Official PEP:** https://peps.python.org/pep-0484/
**Title:** Type Hints
**Status:** Accepted
**Python Version:** 3.5+
**Authors:** Guido van Rossum, Jukka Lehtosalo, Łukasz Langa

### Overview

PEP 484 introduces a standard syntax for type annotations in Python, enabling static type checking while preserving Python's dynamic nature.

### Key Principles

1. **Optional and Gradual:** Type hints are completely optional
2. **No Runtime Enforcement:** Hints are primarily for static analysis tools
3. **Backward Compatible:** No impact on existing Python code
4. **Tool-Friendly:** Enables better IDE support and linting

### Core Philosophy

> "Type hints should be thought of as a very powerful linter, not as a runtime type enforcement mechanism."

Type hints are annotations, not declarations. Python remains dynamically typed at runtime.

---

### Basic Type Annotations

#### Function Signatures

```python
def greeting(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

def process_data(data: dict) -> None:
    """Returns None explicitly"""
    print(data)
```

#### Variable Annotations

```python
# Simple types
age: int = 30
name: str = "Alice"
is_active: bool = True
score: float = 95.5

# Without initialization
user_id: int
```

---

### The `typing` Module

**Official Documentation:** https://docs.python.org/3/library/typing.html

#### Common Types

```python
from typing import (
    List, Dict, Set, Tuple,
    Optional, Union, Any,
    Callable, TypeVar, Generic
)

# Collections
names: List[str] = ["Alice", "Bob"]
user_data: Dict[str, int] = {"age": 30, "score": 100}
unique_ids: Set[int] = {1, 2, 3}
coordinates: Tuple[float, float] = (10.5, 20.3)

# Optional (None possible)
user_name: Optional[str] = None  # Equivalent to Union[str, None]

# Union (multiple types)
user_id: Union[int, str] = "user_123"

# Any (any type accepted)
data: Any = {"could": "be", "anything": True}
```

#### Advanced Types

**Callable:**
```python
from typing import Callable

def apply_function(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# Callable[[arg_types...], return_type]
callback: Callable[[str], None]
```

**Type Aliases:**
```python
from typing import List, Dict, Tuple

# Define reusable type aliases
UserId = int
UserData = Dict[str, Union[str, int]]
Coordinates = Tuple[float, float]
PathList = List[Tuple[str, str]]

def get_user(user_id: UserId) -> UserData:
    return {"name": "Alice", "age": 30}
```

**Generic Types:**
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')  # Generic type variable

class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

# Usage
int_stack: Stack[int] = Stack()
str_stack: Stack[str] = Stack()
```

---

### Forward References

For types not yet defined, use string literals:

```python
class Node:
    def __init__(self, value: int, next: 'Node' = None):
        self.value = value
        self.next = next  # Node defined before this line

# Python 3.7+ with __future__
from __future__ import annotations

class Node:
    def __init__(self, value: int, next: Node = None):  # No quotes needed
        self.value = value
        self.next = next
```

---

### Protocol (Structural Subtyping)

**PEP 544:** https://peps.python.org/pep-0544/

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

def render(obj: Drawable) -> None:  # Duck typing with type checking
    obj.draw()

render(Circle())  # OK - Circle has draw() method
```

---

### Modern Type Hints (Python 3.9+)

**PEP 585:** Built-in Generic Types

```python
# Python 3.9+ - Use built-in types directly
names: list[str] = ["Alice", "Bob"]  # Instead of List[str]
user_data: dict[str, int] = {"age": 30}  # Instead of Dict[str, int]
coordinates: tuple[float, float] = (10.5, 20.3)  # Instead of Tuple

# Optional with None
name: str | None = None  # Instead of Optional[str]

# Union types
user_id: int | str = 123  # Instead of Union[int, str]
```

**PEP 604:** Union Operator

```python
# Old style (3.5-3.9)
from typing import Union
value: Union[int, str, None]

# New style (3.10+)
value: int | str | None
```

---

### Type Checking Tools

**mypy:**
```bash
pip install mypy
mypy your_script.py
```

**pyright (Microsoft):**
```bash
pip install pyright
pyright your_script.py
```

**pyre (Facebook):**
```bash
pip install pyre-check
pyre check
```

---

### Best Practices for Type Hints

#### 1. Annotate Public APIs

```python
# Good - Public function fully annotated
def calculate_total(items: list[dict[str, float]], tax_rate: float) -> float:
    return sum(item["price"] for item in items) * (1 + tax_rate)

# Private functions can have fewer annotations
def _helper(data):
    return data.process()
```

#### 2. Use Type Aliases for Complex Types

```python
# Bad - Repetitive and hard to read
def process_data(data: Dict[str, List[Tuple[int, str, float]]]) -> Dict[str, List[Tuple[int, str, float]]]:
    pass

# Good - Clear and reusable
UserRecords = Dict[str, List[Tuple[int, str, float]]]

def process_data(data: UserRecords) -> UserRecords:
    pass
```

#### 3. Prefer Specific Types Over `Any`

```python
# Bad
def process(data: Any) -> Any:
    return data.transform()

# Good
from typing import Protocol

class Transformable(Protocol):
    def transform(self) -> dict:
        ...

def process(data: Transformable) -> dict:
    return data.transform()
```

#### 4. Use `Optional` for Nullable Values

```python
# Good - Explicit about None possibility
def find_user(user_id: int) -> Optional[User]:
    user = db.query(user_id)
    return user if user else None
```

#### 5. Annotate Class Attributes

```python
class User:
    name: str
    age: int
    email: Optional[str] = None

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

---

## Async/Await Standards (PEP 492)

**Official PEP:** https://peps.python.org/pep-0492/
**Title:** Coroutines with async and await syntax
**Status:** Final
**Python Version:** 3.5+
**Authors:** Yury Selivanov

### Overview

PEP 492 introduces native coroutine syntax with `async def` and `await`, making asynchronous Python code more readable and Pythonic.

### Motivation

- **Prior to PEP 492:** Generator-based coroutines (`@asyncio.coroutine` decorator)
- **PEP 492 Goal:** First-class syntax for async programming
- **Foundation:** Built on PEP 3156 (asyncio)

---

### Native Coroutines

#### Basic Syntax

```python
import asyncio

# Define async function (coroutine)
async def fetch_data(url: str) -> dict:
    await asyncio.sleep(1)  # Simulate I/O operation
    return {"url": url, "data": "content"}

# Call coroutine
async def main():
    result = await fetch_data("https://example.com")
    print(result)

# Run event loop
asyncio.run(main())
```

#### Key Rules

1. **`async def`** creates a native coroutine
2. **`await`** can only be used inside `async def` functions
3. **`yield`/`yield from`** are SyntaxError in `async def`
4. Calling `async def` returns a coroutine object (must be awaited)

---

### Async Context Managers

**PEP 492 introduces:** `async with`

```python
class AsyncResource:
    async def __aenter__(self):
        print("Acquiring resource")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Releasing resource")
        await asyncio.sleep(0.1)

async def use_resource():
    async with AsyncResource() as resource:
        print("Using resource")
```

**Real-world example:**
```python
import aiohttp

async def fetch_url(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

---

### Async Iterators

**PEP 492 introduces:** `async for`

```python
class AsyncRange:
    def __init__(self, stop: int):
        self.stop = stop
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)  # Simulate async work
        self.current += 1
        return self.current - 1

async def main():
    async for num in AsyncRange(5):
        print(num)
```

**Real-world example:**
```python
async def process_stream(stream):
    async for chunk in stream:
        await process_chunk(chunk)
```

---

### Async Comprehensions (PEP 530)

**PEP 530:** https://peps.python.org/pep-0530/
**Python Version:** 3.6+

```python
# Async list comprehension
results = [await fetch(url) async for url in url_stream]

# Async dict comprehension
data = {url: await fetch(url) async for url in url_stream}

# Async set comprehension
unique = {await process(item) async for item in items}
```

---

### Async Generators (PEP 525)

**PEP 525:** https://peps.python.org/pep-0525/
**Python Version:** 3.6+

```python
async def async_range(stop: int):
    for i in range(stop):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_range(5):
        print(num)
```

---

### asyncio Library

**Official Documentation:** https://docs.python.org/3/library/asyncio.html

#### Core Concepts

**Event Loop:**
```python
import asyncio

# Python 3.7+
asyncio.run(main())  # Recommended

# Python 3.6 and older
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

**Tasks:**
```python
async def task1():
    await asyncio.sleep(1)
    return "Task 1 done"

async def task2():
    await asyncio.sleep(2)
    return "Task 2 done"

async def main():
    # Run concurrently
    results = await asyncio.gather(task1(), task2())
    print(results)  # ['Task 1 done', 'Task 2 done']
```

**Create Task:**
```python
async def main():
    # Schedule task to run concurrently
    task = asyncio.create_task(fetch_data("url"))

    # Do other work
    await other_work()

    # Wait for task
    result = await task
```

**Timeout:**
```python
async def fetch_with_timeout(url: str) -> str:
    try:
        async with asyncio.timeout(5.0):  # Python 3.11+
            return await fetch(url)
    except asyncio.TimeoutError:
        return "Timeout"

# Python 3.10 and older
async def fetch_with_timeout_old(url: str) -> str:
    try:
        return await asyncio.wait_for(fetch(url), timeout=5.0)
    except asyncio.TimeoutError:
        return "Timeout"
```

---

### Type Hints for Async Code

```python
from typing import Coroutine, Awaitable, AsyncIterator
import asyncio

# Coroutine type hint
async def fetch_data(url: str) -> dict:
    await asyncio.sleep(1)
    return {"data": "content"}

# Function returning coroutine
def get_fetcher(url: str) -> Coroutine[None, None, dict]:
    return fetch_data(url)

# Awaitable (more general)
def schedule_fetch(url: str) -> Awaitable[dict]:
    return asyncio.create_task(fetch_data(url))

# Async iterator
async def async_range(n: int) -> AsyncIterator[int]:
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i
```

---

### Best Practices for Async Code

#### 1. Use `asyncio.run()` for Entry Point

```python
# Good
async def main():
    await application_logic()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 2. Avoid Blocking Calls in Async Functions

```python
# Bad - blocks event loop
async def bad_example():
    time.sleep(5)  # Blocks entire event loop!
    return "done"

# Good - yields control
async def good_example():
    await asyncio.sleep(5)  # Other tasks can run
    return "done"
```

#### 3. Use `asyncio.gather()` for Concurrent Execution

```python
# Bad - sequential execution
async def sequential():
    result1 = await fetch(url1)  # Wait
    result2 = await fetch(url2)  # Wait
    return [result1, result2]

# Good - concurrent execution
async def concurrent():
    results = await asyncio.gather(
        fetch(url1),  # Start immediately
        fetch(url2),  # Start immediately
    )
    return results
```

#### 4. Handle Errors in Concurrent Tasks

```python
async def safe_concurrent():
    results = await asyncio.gather(
        fetch(url1),
        fetch(url2),
        return_exceptions=True  # Don't fail on first error
    )

    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")
        else:
            print(f"Success: {result}")
```

#### 5. Use Async Context Managers for Resources

```python
# Good - proper resource cleanup
async def fetch_all(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

---

## Python Enhancement Proposals (PEPs)

### Type System Evolution

| PEP | Title | Python | Status |
|-----|-------|--------|--------|
| [PEP 484](https://peps.python.org/pep-0484/) | Type Hints | 3.5 | Final |
| [PEP 526](https://peps.python.org/pep-0526/) | Syntax for Variable Annotations | 3.6 | Final |
| [PEP 544](https://peps.python.org/pep-0544/) | Protocols: Structural subtyping | 3.8 | Final |
| [PEP 585](https://peps.python.org/pep-0585/) | Type Hinting Generics In Standard Collections | 3.9 | Final |
| [PEP 604](https://peps.python.org/pep-0604/) | Allow writing union types as X \| Y | 3.10 | Final |
| [PEP 612](https://peps.python.org/pep-0612/) | Parameter Specification Variables | 3.10 | Final |
| [PEP 613](https://peps.python.org/pep-0613/) | Explicit Type Aliases | 3.10 | Final |
| [PEP 646](https://peps.python.org/pep-0646/) | Variadic Generics | 3.11 | Final |
| [PEP 673](https://peps.python.org/pep-0673/) | Self Type | 3.11 | Final |
| [PEP 675](https://peps.python.org/pep-0675/) | Arbitrary Literal String Type | 3.11 | Final |

### Async/Await Evolution

| PEP | Title | Python | Status |
|-----|-------|--------|--------|
| [PEP 3156](https://peps.python.org/pep-3156/) | Asynchronous IO Support Rebooted: "asyncio" | 3.4 | Final |
| [PEP 492](https://peps.python.org/pep-0492/) | Coroutines with async and await syntax | 3.5 | Final |
| [PEP 525](https://peps.python.org/pep-0525/) | Asynchronous Generators | 3.6 | Final |
| [PEP 530](https://peps.python.org/pep-0530/) | Asynchronous Comprehensions | 3.6 | Final |

### Code Quality PEPs

| PEP | Title | Status |
|-----|-------|--------|
| [PEP 8](https://peps.python.org/pep-0008/) | Style Guide for Python Code | Active |
| [PEP 20](https://peps.python.org/pep-0020/) | The Zen of Python | Active |
| [PEP 257](https://peps.python.org/pep-0257/) | Docstring Conventions | Active |

---

## Best Practices

### Code Style (PEP 8)

**Official Guide:** https://peps.python.org/pep-0008/

#### Key Points

**Indentation:**
- 4 spaces per indentation level
- Never mix tabs and spaces

**Line Length:**
- Maximum 79 characters for code
- Maximum 72 for docstrings/comments

**Naming Conventions:**
- `snake_case` for functions, variables, methods
- `PascalCase` for classes
- `UPPER_CASE` for constants
- `_leading_underscore` for internal use

**Imports:**
```python
# Standard library
import os
import sys

# Third-party
import numpy as np
import pandas as pd

# Local application
from myapp.models import User
from myapp.utils import helper
```

---

### Docstrings (PEP 257 + Google Style)

**Official PEP:** https://peps.python.org/pep-0257/

**Google Style Guide:** https://google.github.io/styleguide/pyguide.html

```python
def calculate_total(
    items: list[dict[str, float]],
    tax_rate: float,
    discount: float = 0.0
) -> float:
    """Calculate total price with tax and discount.

    Args:
        items: List of item dictionaries with 'price' key
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
        discount: Discount as decimal (e.g., 0.1 for 10% off)

    Returns:
        Total price after tax and discount

    Raises:
        ValueError: If tax_rate or discount is negative

    Example:
        >>> items = [{"price": 10.0}, {"price": 20.0}]
        >>> calculate_total(items, tax_rate=0.08, discount=0.1)
        29.16
    """
    if tax_rate < 0 or discount < 0:
        raise ValueError("Tax rate and discount must be non-negative")

    subtotal = sum(item["price"] for item in items)
    after_discount = subtotal * (1 - discount)
    return after_discount * (1 + tax_rate)
```

---

### Modern Python Features (3.10+)

**Match Statement (PEP 634):**
```python
def handle_response(status_code: int) -> str:
    match status_code:
        case 200:
            return "Success"
        case 404:
            return "Not Found"
        case 500 | 502 | 503:
            return "Server Error"
        case _:
            return "Unknown"
```

**Structural Pattern Matching:**
```python
def process_data(data: dict) -> str:
    match data:
        case {"type": "user", "id": user_id}:
            return f"User: {user_id}"
        case {"type": "product", "sku": sku}:
            return f"Product: {sku}"
        case _:
            return "Unknown data type"
```

---

## Tools & Ecosystem

### Type Checking

- **mypy:** https://mypy.readthedocs.io/
- **pyright:** https://github.com/microsoft/pyright
- **pyre:** https://pyre-check.org/

### Code Formatting

- **black:** https://black.readthedocs.io/ (opinionated, PEP 8 compliant)
- **autopep8:** https://github.com/hhatto/autopep8

### Linting

- **ruff:** https://github.com/astral-sh/ruff (fast, modern)
- **flake8:** https://flake8.pycqa.org/
- **pylint:** https://pylint.pycqa.org/

### Import Sorting

- **isort:** https://pycqa.github.io/isort/

---

## References

### Official Python Documentation

1. **PEP Index:** https://peps.python.org/
2. **typing module:** https://docs.python.org/3/library/typing.html
3. **asyncio:** https://docs.python.org/3/library/asyncio.html
4. **Style Guide (PEP 8):** https://peps.python.org/pep-0008/

### Key PEPs

1. **PEP 484 (Type Hints):** https://peps.python.org/pep-0484/
2. **PEP 492 (async/await):** https://peps.python.org/pep-0492/
3. **PEP 585 (Generic Types):** https://peps.python.org/pep-0585/
4. **PEP 604 (Union Operator):** https://peps.python.org/pep-0604/

### Best Practices

1. **Google Python Style Guide:** https://google.github.io/styleguide/pyguide.html
2. **Real Python:** https://realpython.com/
3. **Python Packaging Guide:** https://packaging.python.org/

---

**Last Updated:** 2025-10-06
**Research Quality:** Tier 1 (Official PEPs and Python.org)
**Python Versions Covered:** 3.5 - 3.13
