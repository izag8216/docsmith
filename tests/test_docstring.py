"""Tests for docstring module."""

import pytest
from docsmith.docstring import (
    detect_format,
    parse,
    DocstringFormat,
    _parse_google,
    _parse_numpy,
    _parse_sphinx,
    _extract_google_args,
    _extract_numpy_params,
)


def test_detect_format_auto_google():
    """Test auto-detection of Google format."""
    doc = """Summary line.

    Args:
        x: Description.
    """
    assert detect_format(doc) == DocstringFormat.GOOGLE


def test_detect_format_auto_numpy():
    """Test auto-detection of NumPy format."""
    doc = """Summary line.

    Parameters
    ----------
    x : type
        Description.
    """
    assert detect_format(doc) == DocstringFormat.NUMPY


def test_detect_format_auto_sphinx():
    """Test auto-detection of Sphinx format."""
    doc = """Summary line.

    :param x: Description.
    """
    assert detect_format(doc) == DocstringFormat.SPHINX


def test_detect_format_empty():
    """Test detection with empty docstring."""
    assert detect_format("") == DocstringFormat.GOOGLE
    assert detect_format(None) == DocstringFormat.GOOGLE


def test_parse_google_complete():
    """Test parsing a complete Google-style docstring."""
    docstring = """Short summary.

    Longer description that spans
    multiple lines.

    Args:
        x: Description of x.
        y: Description of y.

    Returns:
        The return value.

    Raises:
        ValueError: When something fails.
    """

    result = parse(docstring, DocstringFormat.GOOGLE)

    assert "Short summary" in result["description"]
    assert len(result["args"]) == 2
    assert result["args"][0] == ("x", "Description of x.")
    assert result["returns"] == "The return value."
    assert any("ValueError" in r for r in result["raises"])


def test_parse_google_no_args():
    """Test parsing Google-style with no args."""
    docstring = """Simple function.

    Returns:
        None.
    """

    result = parse(docstring, DocstringFormat.GOOGLE)

    assert "Simple function" in result["description"]
    assert result["args"] == []
    assert result["returns"] == "None."


def test_extract_google_args_basic():
    """Test extracting Google-style arguments."""
    lines = [
        "x: Description of x.",
        "    More description on next line.",
        "y: Description of y.",
    ]

    args = _extract_google_args(lines)

    assert len(args) == 2
    assert args[0] == ("x", "Description of x. More description on next line.")
    assert args[1] == ("y", "Description of y.")


def test_extract_google_args_empty():
    """Test extracting from empty lines."""
    args = _extract_google_args([])
    assert args == []


def test_parse_numpy_complete():
    """Test parsing a complete NumPy-style docstring."""
    docstring = """Short summary.

    Longer description here.

    Parameters
    ----------
    x : int
        Description of x.
    y : str
        Description of y.

    Returns
    -------
    bool
        The return value.
    """

    result = parse(docstring, DocstringFormat.NUMPY)

    assert "Short summary" in result["description"]
    assert len(result["args"]) == 2
    assert result["args"][0][0] == "x"
    assert result["args"][1][0] == "y"
    assert "bool" in result["returns"]


def test_parse_numpy_no_params():
    """Test parsing NumPy-style without parameters."""
    docstring = """Just returns something.

    Returns
    -------
    int
        A number.
    """

    result = parse(docstring, DocstringFormat.NUMPY)

    assert result["args"] == []
    assert result["returns"] is not None and len(result["returns"]) > 0


def test_extract_numpy_params_basic():
    """Test extracting NumPy-style parameters."""
    lines = [
        "x : int",
        "    Description of x.",
        "y : str",
        "    Description of y.",
    ]

    params = _extract_numpy_params(lines)

    assert len(params) == 2
    assert params[0][0] == "x"
    assert params[1][0] == "y"


def test_parse_sphinx_complete():
    """Test parsing a complete Sphinx-style docstring."""
    docstring = """Short summary.

    :param x: Description of x.
    :param y: Description of y.
    :returns: The return value.
    :raises ValueError: When something fails.
    """

    result = parse(docstring, DocstringFormat.SPHINX)

    assert "Short summary" in result["description"]
    assert len(result["args"]) >= 1
    assert result["args"][0][0] in ("x", "y")
    assert result["returns"] is not None


def test_parse_sphinx_no_params():
    """Test parsing Sphinx-style without params."""
    docstring = """Simple function.

    :returns: Nothing useful.
    """

    result = parse(docstring, DocstringFormat.SPHINX)

    assert result["args"] == []
    assert result["returns"] == "Nothing useful."


def test_parse_auto_detection():
    """Test auto-detection through parse function."""
    google_doc = """Function.

    Args:
        x: Description.
    """
    result = parse(google_doc, DocstringFormat.AUTO)
    assert result["args"][0][0] == "x"

    numpy_doc = """Function.

    Parameters
    ----------
    x : type
        Description.
    ----------
    """
    result = parse(numpy_doc, DocstringFormat.AUTO)
    assert len(result["args"]) == 1


def test_docstring_enum_values():
    """Test DocstringFormat enum values."""
    assert DocstringFormat.GOOGLE.value == "google"
    assert DocstringFormat.NUMPY.value == "numpy"
    assert DocstringFormat.SPHINX.value == "sphinx"
    assert DocstringFormat.AUTO.value == "auto"