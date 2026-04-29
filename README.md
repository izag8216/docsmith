# docsmith

[![header](https://raw.githubusercontent.com/izag8216/docsmith/main/docs/docsmith-header.svg)](https://github.com/izag8216/docsmith)

**Lightweight docstring to Markdown API documentation generator.**

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-29A745?style=for-the-badge&logo=license&logoColor=white)
![PyPI](https://img.shields.io/badge/PyPI-v0.1.0-4B8BBE?style=for-the-badge&logo=pypi&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-80%25%2B-FF6B6B?style=for-the-badge&logo=test&logoColor=white)

## Overview

docsmith parses Python source files using the `ast` module to extract docstrings, type annotations, and code structure **without importing the code**. It renders clean Markdown documentation using customizable Jinja2 templates, supporting Google, NumPy, and Sphinx docstring formats.

Unlike Sphinx (which requires reStructuredText and complex configuration) or `pdoc` (which imports your code and may cause side effects), docsmith provides a lightweight, zero-side-effect solution for generating API documentation.

## Installation

```bash
pip install docsmith
```

Or install from source:

```bash
git clone https://github.com/izag8216/docsmith.git
cd docsmith
pip install -e .
```

## Quick Start

### Generate documentation for a directory

```bash
docsmith generate ./src --format google --output docs/api.md
```

### Generate for a single module

```bash
docsmith single path/to/module.py --output api.md
```

### Serve with live reload

```bash
docsmith serve ./src --port 8090 --watch
```

### Check documentation coverage

```bash
docsmith diff old_docs.md new_docs.md --check-coverage
```

## Features

- **AST-based parsing**: Extract docstrings without importing code (zero side effects)
- **Multi-format support**: Google, NumPy, and Sphinx docstring formats
- **Jinja2 templating**: Fully customizable output templates
- **Coverage diff**: Compare old vs new docs for API surface changes
- **Watch mode**: Auto-regenerate docs on file changes

## Supported Docstring Formats

### Google Style

```python
def func(arg1, arg2):
    """Summary line.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.

    Returns:
        Description of return value.
    """
```

### NumPy Style

```python
def func(arg1, arg2):
    """
    Summary line.

    Parameters
    ----------
    arg1 : type
        Description of arg1.
    arg2 : type
        Description of arg2.

    Returns
    -------
    type
        Description of return value.
    """
```

### Sphinx Style

```python
def func(arg1, arg2):
    """
    Summary line.

    :param arg1: Description of arg1.
    :param arg2: Description of arg2.
    :returns: Description of return value.
    """
```

## Custom Templates

Use Jinja2 templates for custom output:

```bash
docsmith generate ./src --template docs/my_template.j2 --output docs/api.md
```

## Configuration

Initialize a configuration file:

```bash
docsmith init
```

This creates a `.docsmith.toml` in the current directory.

## CLI Commands

| Command | Description |
|---------|-------------|
| `generate` | Generate documentation for Python source files |
| `single` | Generate documentation for a single module |
| `serve` | Serve documentation with live reload |
| `diff` | Compare two documentation files for API surface changes |
| `init` | Initialize a docsmith configuration file |

## Development

### Setup

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=docsmith --cov-report=term-missing --cov-fail-under=80
```

### Linting

```bash
black src/
ruff check src/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Documentation](docs/)
- [API Reference](docs/api.md)
- [Usage Guide](docs/usage.md)