# PRD -- docsmith

> Lightweight Docstring to Markdown API Documentation Generator

## 1. Concept & Vision

docsmith is a zero-dependency-side-effect Python documentation generator that parses source files via AST to extract docstrings, type annotations, and code structure without importing the code. It renders clean Markdown documentation using customizable Jinja2 templates, supporting Google, NumPy, and Sphinx docstring formats.

**Feel:** Fast, precise, surgical. Like a skilled typesetter -- takes raw manuscript and produces beautiful printed output without altering the original. No framework overhead, no configuration obsession, no magic.

---

## 2. Problem Statement

- **Sphinx** requires reStructuredText, conf.py, and extensions -- overkill for small libraries
- **pdoc** imports code, causing potential side effects in user code
- **pydoc** generates ugly text/HTML output
- **mkdocstrings** requires MkDocs infrastructure
- **No lightweight tool** parses docstrings via AST (zero imports), supports multiple formats, and outputs Markdown with Jinja2 templates

---

## 3. Solution

### Core Features

| Feature | Description |
|---------|-------------|
| AST-based parsing | Uses Python's `ast` module to extract docstrings without importing code |
| Multi-format support | Google, NumPy, and Sphinx docstring formats |
| Jinja2 templating | Fully customizable output templates |
| CLI interface | `generate`, `single`, `serve`, `diff` commands |
| Watch mode | Auto-regenerate docs on file changes |
| Coverage diff | Compare old vs new docs for API surface changes |

### Commands

```bash
# Generate documentation for a directory
docsmith generate ./src --format google --output docs/api.md

# Generate for a single module
docsmith single module.py --template custom.md.j2

# Serve with live reload
docsmith serve ./src --port 8090 --watch

# Check documentation coverage
docsmith diff old.md new.md --check-coverage
```

---

## 4. Target Users

- Python library authors who want clean API docs without Sphinx complexity
- Small project maintainers needing lightweight documentation
- Developers who want customizable Jinja2 templates for docs
- Teams with multiple docstring formats (Google/NumPy/Sphinx mixed codebases)

---

## 5. Technical Approach

### Architecture

```
src/
├── cli.py              # Click-based CLI interface
├── core/
│   ├── __init__.py
│   ├── parser.py       # AST parser for docstring extraction
│   ├── formatter.py    # Markdown output formatter
│   ├── template.py     # Jinja2 template engine
│   └── docstring.py    # Docstring format detection (Google/NumPy/Sphinx)
└── templates/          # Default Jinja2 templates
    ├── markdown.j2
    └── function.j2
```

### Dependencies

| Package | Version | Rationale |
|---------|---------|-----------|
| click | >=8.0 | CLI framework |
| jinja2 | >=3.0 | Template engine |
| watchdog | >=3.0 | File watching for serve command |

All dependencies are standard -- no exotic choices.

### Output Formats

- Markdown (default) -- clean GitHub-compatible output
- Custom templates via Jinja2 for full control

---

## 6. Docstring Format Support

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

---

## 7. Milestones

### M1: Core AST Parser
- Parse Python files using `ast` module
- Extract docstrings from modules, classes, and functions
- Extract type annotations from function signatures
- Handle all three docstring formats (Google, NumPy, Sphinx)

### M2: Template Engine
- Jinja2 integration for customizable output
- Default markdown template
- Include/exclude options for modules, classes, functions

### M3: CLI Interface
- `generate` command for batch processing
- `single` command for single file
- `serve` command with watchdog for live reload
- `diff` command for coverage checking

### M4: Polish & Publishing
- Test coverage >80%
- i18n READMEs (en + ja)
- Custom SVG header
- GitHub publication

---

## 8. Out of Scope

- Importing code (ast-only parsing, no imports)
- reStructuredText support (Markdown only)
- HTML/PDF output (Markdown only, external converters can handle)
- Interactive documentation browser (static output only)

---

## 9. Testing Strategy

| Layer | Framework | Target |
|-------|-----------|--------|
| Unit | pytest | Core parser, formatter, template functions |
| Integration | pytest | CLI commands, file I/O |

Coverage target: **80%+** for all Python files.

---

## 10. File Structure

```
docsmith/
├── src/
│   ├── docsmith/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── cli.py
│   │   ├── parser.py
│   │   ├── formatter.py
│   │   ├── template.py
│   │   └── docstring.py
│   └── templates/
│       └── default.j2
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_formatter.py
│   ├── test_docstring.py
│   └── test_cli.py
├── examples/
│   ├── example_module.py
│   └── example_output.md
├── docs/
│   ├── usage.md
│   └── api.md
├── pyproject.toml
├── README.md
├── README-ja.md
├── LICENSE (MIT)
├── CONTRIBUTING.md
├── THIRD_PARTY_LICENSES.md
└── .gitignore
```