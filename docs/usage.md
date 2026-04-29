# Usage

## Installation

```bash
pip install docsmith
```

## Quick Start

### Generate documentation for a directory

```bash
docsmith generate ./src --format google --output docs/api.md
```

### Generate documentation for a single module

```bash
docsmith single path/to/module.py --output api.md
```

### Serve documentation with live reload

```bash
docsmith serve ./src --port 8090 --watch
```

### Check documentation coverage

```bash
docsmith diff old_docs.md new_docs.md --check-coverage
```

## Docstring Formats

docsmith supports three docstring formats:

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

This creates a `.docsmith.toml` file in the current directory.