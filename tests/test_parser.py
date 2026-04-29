"""Tests for parser module."""

import pytest
from docsmith.parser import (
    parse_module,
    parse_function,
    parse_class,
    ModuleDoc,
    ClassDoc,
    FunctionDoc,
    Arg,
)


SAMPLE_MODULE = '''
"""Sample module for testing."""

def hello(name: str) -> str:
    """Say hello to someone.

    Args:
        name: The person to greet.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"


class Calculator:
    """A simple calculator class."""

    def __init__(self):
        """Initialize the calculator."""
        self.result = 0

    def add(self, a: int, b: int) -> int:
        """Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            The sum of a and b.
        """
        return a + b
'''


def test_parse_function_basic():
    """Test parsing a basic function."""
    import ast
    tree = ast.parse(SAMPLE_MODULE)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "hello":
            func_node = node
            break

    assert func_node is not None
    func_doc = parse_function(func_node)

    assert func_doc.name == "hello"
    assert len(func_doc.args) == 1
    assert func_doc.args[0].name == "name"
    assert func_doc.args[0].annotation == "str"
    assert func_doc.returns == "str"
    assert "Say hello" in func_doc.docstring


def test_parse_class_basic():
    """Test parsing a basic class."""
    import ast
    tree = ast.parse(SAMPLE_MODULE)

    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Calculator":
            class_node = node
            break

    assert class_node is not None
    class_doc = parse_class(class_node)

    assert class_doc.name == "Calculator"
    assert "calculator" in class_doc.docstring.lower()
    assert len(class_doc.methods) == 2


def test_arg_dataclass():
    """Test Arg dataclass."""
    arg = Arg(name="x", annotation="int", default="0")
    assert arg.name == "x"
    assert arg.annotation == "int"
    assert arg.default == "0"


def test_function_doc_dataclass():
    """Test FunctionDoc dataclass."""
    func = FunctionDoc(
        name="test",
        docstring="Test function",
        args=[Arg(name="x")],
        returns="int",
    )
    assert func.name == "test"
    assert func.docstring == "Test function"
    assert len(func.args) == 1
    assert func.returns == "int"


def test_class_doc_dataclass():
    """Test ClassDoc dataclass."""
    cls = ClassDoc(
        name="MyClass",
        docstring="A test class",
        methods=[],
        bases=["BaseClass"],
    )
    assert cls.name == "MyClass"
    assert cls.bases == ["BaseClass"]


def test_module_doc_dataclass():
    """Test ModuleDoc dataclass."""
    module = ModuleDoc(
        path="/path/to/module.py",
        docstring="Module docstring",
        classes=[],
        functions=[],
    )
    assert module.path == "/path/to/module.py"
    assert module.docstring == "Module docstring"


SAMPLE_NUMPY = '''
"""NumPy style module."""

def process_data(data, iterations=10):
    \"\"\"
    Process data with iterations.

    Parameters
    ----------
    data : array
        Input data array.
    iterations : int
        Number of iterations to run.

    Returns
    -------
    array
        Processed data.
    \"\"\"
    return data
'''


def test_parse_numpy_docstring():
    """Test parsing NumPy-style docstring."""
    from docsmith.docstring import parse, DocstringFormat

    docstring = '''Process data with iterations.

    Parameters
    ----------
    data : array
        Input data array.
    iterations : int
        Number of iterations to run.

    Returns
    -------
    array
        Processed data.
    '''

    result = parse(docstring, DocstringFormat.NUMPY)

    assert "Process data" in result["description"]
    assert len(result["args"]) == 2
    assert result["args"][0][0] == "data"
    assert result["args"][1][0] == "iterations"


SAMPLE_SPHINX = '''
"""Sphinx style module."""

def legacy_func(x, y):
    """
    Legacy function using Sphinx style.

    :param x: First parameter
    :param y: Second parameter
    :returns: Sum of x and y
    """
    return x + y
'''


def test_parse_sphinx_docstring():
    """Test parsing Sphinx-style docstring."""
    from docsmith.docstring import parse, DocstringFormat

    docstring = '''Legacy function using Sphinx style.

    :param x: First parameter
    :param y: Second parameter
    :returns: Sum of x and y
    '''

    result = parse(docstring, DocstringFormat.SPHINX)

    assert "Legacy function" in result["description"]
    assert len(result["args"]) == 2
    assert result["args"][0][0] == "x"
    assert result["args"][1][0] == "y"
    assert result["returns"] == "Sum of x and y"


def test_detect_format_google():
    """Test format detection for Google style."""
    from docsmith.docstring import detect_format, DocstringFormat

    docstring = """Function description.

    Args:
        x: Description of x.
    """
    assert detect_format(docstring) == DocstringFormat.GOOGLE


def test_detect_format_numpy():
    """Test format detection for NumPy style."""
    from docsmith.docstring import detect_format, DocstringFormat

    docstring = """Function description.

    Parameters
    ----------
    x : type
        Description of x.
    """
    assert detect_format(docstring) == DocstringFormat.NUMPY


def test_detect_format_sphinx():
    """Test format detection for Sphinx style."""
    from docsmith.docstring import detect_format, DocstringFormat

    docstring = """Function description.

    :param x: Description of x.
    """
    assert detect_format(docstring) == DocstringFormat.SPHINX