"""Tests for formatter module."""

import pytest
from docsmith.formatter import (
    format_module,
    format_class,
    format_function,
    format_modules,
    format_coverage_report,
    _extract_symbols,
)
from docsmith.parser import ModuleDoc, ClassDoc, FunctionDoc, Arg


SIMPLE_MODULE = '''"""A simple module."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


class Calculator:
    """A calculator class."""

    def __init__(self):
        self.result = 0

    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y
'''


def test_format_function_basic():
    """Test formatting a basic function."""
    func = FunctionDoc(
        name="add",
        docstring="Add two numbers.",
        args=[Arg(name="a", annotation="int"), Arg(name="b", annotation="int")],
        returns="int",
    )

    result = format_function(func)

    assert "def add(a: int, b: int) -> int" in result
    assert "Add two numbers" in result


def test_format_function_no_docstring():
    """Test formatting a function without docstring."""
    func = FunctionDoc(name="empty_func")

    result = format_function(func, show_docstring=False)

    assert "def empty_func()" in result


def test_format_function_with_decorators():
    """Test formatting a function with decorators."""
    func = FunctionDoc(
        name="decorated_func",
        decorators=["staticmethod", "cache"],
    )

    result = format_function(func, show_docstring=False)

    assert "@staticmethod" in result
    assert "@cache" in result


def test_format_class_basic():
    """Test formatting a basic class."""
    cls = ClassDoc(
        name="Calculator",
        docstring="A calculator class.",
        methods=[],
    )

    result = format_class(cls)

    assert "### `Calculator`" in result
    assert "A calculator class" in result


def test_format_class_with_bases():
    """Test formatting a class with base classes."""
    cls = ClassDoc(
        name="SpecialCalc",
        bases=["Calculator", "Displayable"],
    )

    result = format_class(cls)

    assert "### `SpecialCalc(Calculator, Displayable)`" in result


def test_format_class_with_methods():
    """Test formatting a class with methods."""
    cls = ClassDoc(
        name="Calculator",
        methods=[
            FunctionDoc(name="add", args=[]),
            FunctionDoc(name="sub", args=[]),
        ],
    )

    result = format_class(cls)

    assert "add" in result
    assert "sub" in result


def test_format_module_basic():
    """Test formatting a basic module."""
    module = ModuleDoc(
        path="test_module.py",
        docstring="Test module.",
        functions=[FunctionDoc(name="test_func", docstring="A test function.")],
    )

    result = format_module(module)

    assert "Module Documentation" in result
    assert "Test module" in result
    assert "test_func" in result


def test_format_module_empty():
    """Test formatting an empty module."""
    module = ModuleDoc(path="empty.py")

    result = format_module(module)

    assert "Module Documentation" in result
    assert len(result.split("\n")) <= 5


def test_extract_symbols():
    """Test extracting symbols from markdown."""
    md = """
### `def add(a, b)`

Some description.

### `def multiply(x, y)`

Another function.

### `class Calculator`
    """
    symbols = _extract_symbols(md)

    assert "def:add" in symbols
    assert "def:multiply" in symbols
    assert "class:Calculator" in symbols


def test_format_coverage_report_no_changes():
    """Test coverage report with no changes."""
    md = """
### `def add(a, b)`
"""

    complete, report = format_coverage_report(md, md)

    assert complete is True
    assert report == ""


def test_format_coverage_report_added():
    """Test coverage report with added symbols."""
    old = "### `def add(a, b)`"
    new = "### `def add(a, b)`\n### `def multiply(x, y)`"

    complete, report = format_coverage_report(old, new)

    assert complete is True
    assert "Added" in report
    assert "def:multiply" in report


def test_format_coverage_report_removed():
    """Test coverage report with removed symbols."""
    old = "### `def add(a, b)`\n### `def multiply(x, y)`"
    new = "### `def add(a, b)`"

    complete, report = format_coverage_report(old, new)

    assert complete is False
    assert "Removed" in report
    assert "def:multiply" in report


def test_format_coverage_report_both():
    """Test coverage report with both additions and removals."""
    old = "### `def old_func()`"
    new = "### `def new_func()`"

    complete, report = format_coverage_report(old, new)

    assert complete is False
    assert "Added" in report
    assert "Removed" in report


def test_format_modules_multiple():
    """Test formatting multiple modules."""
    modules = [
        ModuleDoc(path="module1.py", functions=[FunctionDoc(name="func1")]),
        ModuleDoc(path="module2.py", functions=[FunctionDoc(name="func2")]),
    ]

    result = format_modules(modules)

    assert "module1" in result
    assert "module2" in result
    assert "func1" in result
    assert "func2" in result