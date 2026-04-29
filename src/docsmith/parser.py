"""AST-based Python source parser for docstring extraction."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Arg:
    """Function argument."""

    name: str
    annotation: Optional[str] = None
    default: Optional[str] = None


@dataclass
class FunctionDoc:
    """Documentation for a function or method."""

    name: str
    docstring: str = ""
    args: list[Arg] = field(default_factory=list)
    returns: Optional[str] = None
    raises: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    lineno: int = 0


@dataclass
class ClassDoc:
    """Documentation for a class."""

    name: str
    docstring: str = ""
    methods: list[FunctionDoc] = field(default_factory=list)
    attributes: list[tuple[str, str]] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)
    lineno: int = 0


@dataclass
class ModuleDoc:
    """Documentation for a module."""

    path: str
    docstring: str = ""
    classes: list[ClassDoc] = field(default_factory=list)
    functions: list[FunctionDoc] = field(default_factory=list)


def parse_arg(arg: ast.arg) -> Arg:
    """Parse a function argument from AST."""
    annotation = None
    if arg.annotation:
        annotation = _get_annotation_name(arg.annotation)

    default = None
    if isinstance(arg, ast.arg) and hasattr(arg, 'annotation'):
        default = _get_default_value(arg)

    return Arg(name=arg.arg, annotation=annotation, default=default)


def _get_annotation_name(node: ast.AST) -> str:
    """Get the name of a type annotation."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        parts = []
        cur = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    elif isinstance(node, ast.Subscript):
        base = _get_annotation_name(node.value)
        if node.slice:
            if isinstance(node.slice, ast.Tuple):
                args = ",".join(_get_annotation_name(e) for e in node.slice.elts)
            else:
                args = _get_annotation_name(node.slice)
            return f"{base}[{args}]"
    elif isinstance(node, ast.Constant):
        return repr(node.value)
    return "Any"


def _get_default_value(arg: ast.arg) -> Optional[str]:
    """Get the default value of an argument if present."""
    return None


def _parse_docstring(docstring: str) -> dict:
    """Parse docstring into sections based on format."""
    if not docstring:
        return {}

    lines = docstring.strip().split("\n")
    sections = {}
    current_section = None
    current_content = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("Args:") or stripped.startswith("Arguments:"):
            current_section = "args"
            current_content = []
        elif stripped.startswith("Returns:") or stripped.startswith("Return:"):
            current_section = "returns"
            current_content = []
        elif stripped.startswith("Raises:"):
            current_section = "raises"
            current_content = []
        elif stripped.startswith("Examples:") or stripped.startswith("Example:"):
            current_section = "examples"
            current_content = []
        elif stripped.startswith("Note:") or stripped.startswith("Notes:"):
            current_section = "notes"
            current_content = []
        elif stripped.startswith("Attributes:"):
            current_section = "attributes"
            current_content = []
        elif current_section:
            current_content.append(line)
            sections[current_section] = "\n".join(current_content)

    return sections


def _detect_docstring_format(docstring: str) -> str:
    """Detect docstring format: google, numpy, or sphinx."""
    if not docstring:
        return "google"

    first_lines = docstring.strip().split("\n")[:10]
    text = "\n".join(first_lines).lower()

    if "parameters" in text and ("---" in docstring or "==" in docstring):
        return "numpy"
    elif ":param" in text or ":type" in text or ":return" in text:
        return "sphinx"
    elif "args:" in text or "arguments:" in text:
        return "google"
    return "google"


def _parse_google_args(docstring: str) -> list[tuple[str, str]]:
    """Parse Google-style Args section."""
    args = []
    lines = docstring.split("\n")
    in_args = False
    current_arg = None
    current_desc = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Args:") or stripped.startswith("Arguments:"):
            in_args = True
            continue
        if in_args:
            if stripped and not stripped.startswith("Returns:") and not stripped.startswith("Raises:"):
                if ":" in stripped and not stripped.startswith(" " * 4):
                    if current_arg:
                        args.append((current_arg, " ".join(current_desc).strip()))
                    parts = stripped.split(":", 1)
                    current_arg = parts[0].strip()
                    current_desc = [parts[1].strip()] if len(parts) > 1 else []
                elif current_arg and stripped:
                    current_desc.append(stripped)

    if current_arg:
        args.append((current_arg, " ".join(current_desc).strip()))

    return args


def _parse_numpy_args(docstring: str) -> list[tuple[str, str]]:
    """Parse NumPy-style Parameters section."""
    args = []
    lines = docstring.split("\n")
    in_params = False
    current_arg = None
    current_desc = []

    for line in lines:
        stripped = line.strip()
        if "parameters" in stripped.lower() and "---" in docstring:
            in_params = True
            continue
        if in_params:
            if stripped.startswith("Returns:") or stripped.startswith("--"):
                if current_arg:
                    args.append((current_arg, " ".join(current_desc).strip()))
                in_params = False
            elif ":" in stripped and not stripped.startswith(" " * 4):
                if current_arg:
                    args.append((current_arg, " ".join(current_desc).strip()))
                current_arg = stripped.split(":")[0].strip()
                rest = stripped.split(":", 1)[1].strip()
                current_desc = [rest] if rest else []
            elif current_arg and stripped:
                current_desc.append(stripped)

    if current_arg:
        args.append((current_arg, " ".join(current_desc).strip()))

    return args


def _parse_sphinx_args(docstring: str) -> list[tuple[str, str]]:
    """Parse Sphinx-style :param: directives."""
    args = []
    for line in docstring.split("\n"):
        if ":param" in line or ":type" in line:
            parts = line.split(":")
            if len(parts) >= 2:
                param_part = parts[1].strip()
                if " " in param_part:
                    param_name = param_part.split()[0]
                    desc = " ".join(param_part.split()[1:])
                    args.append((param_name, desc))
    return args


def parse_google_docstring(docstring: str) -> dict:
    """Parse Google-style docstring into structured format."""
    if not docstring:
        return {}

    result = {
        "description": "",
        "args": [],
        "returns": None,
        "raises": [],
        "yields": None,
        "examples": None,
    }

    lines = docstring.strip().split("\n")
    sections = {}
    current_section = "description"
    current_content = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("Args:") or stripped.startswith("Arguments:"):
            if current_content and current_section == "description":
                result["description"] = "\n".join(current_content).strip()
            current_section = "args"
            current_content = []
        elif stripped.startswith("Returns:") or stripped.startswith("Return:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "returns"
            current_content = []
        elif stripped.startswith("Raises:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "raises"
            current_content = []
        elif stripped.startswith("Yields:") or stripped.startswith("Yield:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "yields"
            current_content = []
        elif stripped.startswith("Examples:") or stripped.startswith("Example:"):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = "examples"
            current_content = []
        else:
            current_content.append(stripped)

    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    if "description" in sections:
        result["description"] = sections["description"]
    if "args" in sections:
        result["args"] = _parse_google_args(docstring)
    if "returns" in sections:
        result["returns"] = sections["returns"]
    if "raises" in sections:
        result["raises"] = [r.strip() for r in sections["raises"].split(",")]
    if "yields" in sections:
        result["yields"] = sections["yields"]
    if "examples" in sections:
        result["examples"] = sections["examples"]

    return result


def parse_numpy_docstring(docstring: str) -> dict:
    """Parse NumPy-style docstring into structured format."""
    if not docstring:
        return {}

    result = {
        "description": "",
        "args": [],
        "returns": None,
        "raises": [],
        "yields": None,
        "examples": None,
    }

    sections = {}
    current_section = None
    current_content = []

    lines = docstring.strip().split("\n")
    desc_lines = []

    for line in lines:
        stripped = line.strip()
        if "parameters" in stripped.lower() and "---" in docstring:
            if desc_lines:
                sections["description"] = "\n".join(desc_lines).strip()
            current_section = "args"
            current_content = []
            desc_lines = []
        elif "returns" in stripped.lower() and "---" in docstring:
            if current_section == "args" and current_content:
                result["args"] = _parse_numpy_params(current_content)
            elif desc_lines:
                sections["description"] = "\n".join(desc_lines).strip()
            current_section = "returns"
            current_content = []
            desc_lines = []
        elif stripped.startswith("--"):
            if current_section == "args" and current_content:
                result["args"] = _parse_numpy_params(current_content)
            elif current_section == "returns" and current_content:
                result["returns"] = "\n".join(current_content).strip()
            break
        elif current_section:
            current_content.append(stripped)
        else:
            desc_lines.append(stripped)

    if desc_lines and not sections:
        result["description"] = "\n".join(desc_lines).strip()

    return result


def _parse_numpy_params(content: list[str]) -> list[tuple[str, str]]:
    """Parse NumPy-style parameter list."""
    args = []
    current_arg = None
    current_desc = []

    for line in content:
        if ":" in line and not line.startswith(" " * 4):
            if current_arg:
                args.append((current_arg, " ".join(current_desc).strip()))
            parts = line.split(":", 1)
            current_arg = parts[0].strip()
            current_desc = [parts[1].strip()] if len(parts) > 1 else []
        elif current_arg:
            current_desc.append(line.strip())

    if current_arg:
        args.append((current_arg, " ".join(current_desc).strip()))

    return args


def parse_sphinx_docstring(docstring: str) -> dict:
    """Parse Sphinx-style docstring into structured format."""
    if not docstring:
        return {}

    result = {
        "description": "",
        "args": [],
        "returns": None,
        "raises": [],
        "examples": None,
    }

    lines = docstring.strip().split("\n")
    desc_lines = []
    in_param = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(":param"):
            parts = stripped.split(":", 2)
            if len(parts) >= 3:
                param_type = parts[1].strip()
                param_rest = parts[2].strip()
                if " " in param_rest:
                    param_name = param_rest.split()[0]
                    param_desc = " ".join(param_rest.split()[1:])
                    result["args"].append((param_name, param_desc))
        elif stripped.startswith(":type"):
            pass
        elif stripped.startswith(":return") or stripped.startswith(":returns"):
            if desc_lines:
                result["description"] = "\n".join(desc_lines).strip()
                desc_lines = []
            if ":" in stripped:
                result["returns"] = stripped.split(":", 2)[-1].strip()
        elif stripped.startswith(":raises"):
            if ":" in stripped:
                result["raises"].append(stripped.split(":", 2)[-1].strip())
        elif stripped and not stripped.startswith(" "):
            desc_lines.append(stripped)

    if desc_lines and not result["description"]:
        result["description"] = "\n".join(desc_lines).strip()

    return result


def parse_docstring(docstring: str, format: str = "auto") -> dict:
    """Parse docstring based on format or auto-detection."""
    if format == "auto":
        format = _detect_docstring_format(docstring)

    if format == "numpy":
        return parse_numpy_docstring(docstring)
    elif format == "sphinx":
        return parse_sphinx_docstring(docstring)
    else:
        return parse_google_docstring(docstring)


def parse_function(node: ast.FunctionDef, source_lines: Optional[list[str]] = None) -> FunctionDoc:
    """Parse a function definition into a FunctionDoc."""
    docstring = ast.get_docstring(node) or ""

    args = []
    for arg in node.args.args:
        args.append(Arg(name=arg.arg, annotation=_get_annotation_name(arg.annotation) if arg.annotation else None))

    if node.args.vararg:
        args.append(Arg(name=f"*{node.args.vararg.arg}", annotation=None))

    for kw in node.args.kwonlyargs:
        args.append(Arg(name=kw.arg, annotation=_get_annotation_name(kw.annotation) if kw.annotation else None))

    if node.args.kwarg:
        args.append(Arg(name=f"**{node.args.kwarg.arg}", annotation=None))

    returns = None
    if node.returns:
        returns = _get_annotation_name(node.returns)

    decorators = [d.attr if isinstance(d, ast.Attribute) else (d.id if isinstance(d, ast.Name) else str(d)) for d in node.decorator_list]

    func_doc = FunctionDoc(
        name=node.name,
        docstring=docstring,
        args=args,
        returns=returns,
        raises=[],
        decorators=decorators,
        lineno=node.lineno,
    )

    return func_doc


def parse_class(node: ast.ClassDef, source_lines: Optional[list[str]] = None) -> ClassDoc:
    """Parse a class definition into a ClassDoc."""
    docstring = ast.get_docstring(node) or ""

    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{_get_annotation_name(base)}")

    attributes = []

    class_doc = ClassDoc(
        name=node.name,
        docstring=docstring,
        methods=[],
        attributes=attributes,
        bases=bases,
        lineno=node.lineno,
    )

    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            func_doc = parse_function(item)
            class_doc.methods.append(func_doc)

    return class_doc


def parse_module(filepath: str) -> ModuleDoc:
    """Parse a Python file into a ModuleDoc."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return ModuleDoc(path=filepath, docstring="", classes=[], functions=[])

    docstring = ast.get_docstring(tree) or ""

    module_doc = ModuleDoc(path=filepath, docstring=docstring, classes=[], functions=[])

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_doc = parse_class(node)
            module_doc.classes.append(class_doc)
        elif isinstance(node, ast.FunctionDef):
            func_doc = parse_function(node)
            module_doc.functions.append(func_doc)

    return module_doc


def parse_directory(dirpath: str) -> list[ModuleDoc]:
    """Parse all Python files in a directory."""
    import os

    modules = []
    for root, _, files in os.walk(dirpath):
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("test_"):
                filepath = os.path.join(root, filename)
                module_doc = parse_module(filepath)
                modules.append(module_doc)

    return modules