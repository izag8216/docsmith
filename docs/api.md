# API Reference

## Core Modules

### `docsmith.parser`

AST-based Python source parser.

#### Functions

- `parse_module(filepath: str) -> ModuleDoc` - Parse a Python file
- `parse_directory(dirpath: str) -> list[ModuleDoc]` - Parse all Python files in a directory
- `parse_function(node: ast.FunctionDef) -> FunctionDoc` - Parse a function definition
- `parse_class(node: ast.ClassDef) -> ClassDoc` - Parse a class definition

#### Data Classes

- `ModuleDoc` - Documentation for a module
- `ClassDoc` - Documentation for a class
- `FunctionDoc` - Documentation for a function
- `Arg` - Function argument with name, type, and default

### `docsmith.formatter`

Markdown output formatter.

#### Functions

- `format_module(module: ModuleDoc) -> str` - Format a module into Markdown
- `format_class(cls: ClassDoc) -> str` - Format a class into Markdown
- `format_function(func: FunctionDoc, full: bool = True) -> str` - Format a function into Markdown
- `format_modules(modules: list[ModuleDoc]) -> str` - Format multiple modules
- `format_coverage_report(old_md: str, new_md: str) -> tuple[bool, str]` - Compare documentation

### `docsmith.docstring`

Docstring format detection and parsing.

#### Functions

- `detect_format(docstring: str) -> DocstringFormat` - Auto-detect docstring format
- `parse(docstring: str, format: DocstringFormat = AUTO) -> dict` - Parse docstring into structured dict

#### Enum

- `DocstringFormat.GOOGLE` - Google-style docstrings
- `DocstringFormat.NUMPY` - NumPy-style docstrings
- `DocstringFormat.SPHINX` - Sphinx-style docstrings
- `DocstringFormat.AUTO` - Auto-detect format

### `docsmith.template`

Jinja2 template engine for custom output.

#### Class

- `TemplateEngine` - Main template rendering class

#### Methods

- `render_module(module: ModuleDoc, template_path: str = None) -> str`
- `render_modules(modules: list[ModuleDoc], template_path: str = None) -> str`
- `render_string(template_string: str, context: dict) -> str`

## CLI Commands

### generate

```bash
docsmith generate <path> [OPTIONS]
```

Generate documentation for Python source files.

**Options:**
- `--format, -f` - Docstring format (google, numpy, sphinx, auto)
- `--output, -o` - Output file path
- `--template, -t` - Custom Jinja2 template
- `--recursive, -r` - Process directories recursively

### single

```bash
docsmith single <filepath> [OPTIONS]
```

Generate documentation for a single module.

**Options:**
- `--format, -f` - Docstring format
- `--output, -o` - Output file path
- `--template, -t` - Custom Jinja2 template

### serve

```bash
docsmith serve <path> [OPTIONS]
```

Serve documentation with live reload.

**Options:**
- `--port, -p` - Port to serve on (default: 8090)
- `--host` - Host to bind to (default: localhost)
- `--template, -t` - Custom Jinja2 template

### diff

```bash
docsmith diff <old> <new> [OPTIONS]
```

Compare two documentation files.

**Options:**
- `--check-coverage` - Exit with error if coverage decreased

### init

```bash
docsmith init [OPTIONS]
```

Initialize a docsmith configuration file.