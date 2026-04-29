"""Markdown formatter for docsmith output."""

from __future__ import annotations

from typing import Optional
from docsmith.parser import ModuleDoc, ClassDoc, FunctionDoc


def format_module(module: ModuleDoc) -> str:
    """Format a module into Markdown."""
    lines = []

    lines.append("# Module Documentation\n")

    if module.docstring:
        lines.append(module.docstring.strip())
        lines.append("\n")

    if module.classes:
        lines.append("## Classes\n\n")
        for cls in module.classes:
            lines.append(format_class(cls))
            lines.append("\n")

    if module.functions:
        lines.append("## Functions\n\n")
        for func in module.functions:
            lines.append(format_function(func, full=False))
            lines.append("\n")

    return "\n".join(lines)


def format_class(cls: ClassDoc) -> str:
    """Format a class into Markdown."""
    lines = []

    name = cls.name
    if cls.bases:
        bases_str = ", ".join(cls.bases)
        name += f"({bases_str})"

    lines.append(f"### `{name}`\n")

    if cls.docstring:
        lines.append(cls.docstring.strip())
        lines.append("\n")

    if cls.attributes:
        lines.append("**Attributes:**\n")
        for attr_name, attr_type in cls.attributes:
            if attr_type:
                lines.append(f"- `{attr_name}` ({attr_type})")
            else:
                lines.append(f"- `{attr_name}`")
        lines.append("\n")

    if cls.methods:
        lines.append("**Methods:**\n")
        for method in cls.methods:
            lines.append(format_function(method, full=False, show_docstring=False))
            lines.append("\n")

    return "\n".join(lines)


def format_function(func: FunctionDoc, full: bool = True, show_docstring: bool = True) -> str:
    """Format a function into Markdown."""
    lines = []

    decorators_str = ""
    if func.decorators:
        decorators_str = " ".join([f"@{d}" for d in func.decorators]) + " "

    args_str = _format_args(func.args)
    signature = f"{decorators_str}def {func.name}({args_str})"
    if func.returns:
        signature += f" -> {func.returns}"

    lines.append(f"### `{signature}`\n")

    if show_docstring and func.docstring:
        lines.append(func.docstring.strip())
        lines.append("\n")

    if full and func.args:
        lines.append("**Parameters:**\n")
        for arg in func.args:
            if arg.annotation:
                lines.append(f"- `{arg.name}` ({arg.annotation})")
            else:
                lines.append(f"- `{arg.name}`")
        lines.append("\n")

    if full and func.raises:
        lines.append("**Raises:**\n")
        for exc in func.raises:
            lines.append(f"- `{exc}`")
        lines.append("\n")

    return "\n".join(lines)


def _format_args(args: list) -> str:
    """Format function arguments."""
    parts = []
    for arg in args:
        if arg.default:
            parts.append(f"{arg.name}={arg.default}")
        elif arg.annotation:
            parts.append(f"{arg.name}: {arg.annotation}")
        else:
            parts.append(arg.name)
    return ", ".join(parts)


def format_modules(modules: list[ModuleDoc]) -> str:
    """Format multiple modules into a single Markdown document."""
    lines = ["# API Documentation\n"]

    for i, module in enumerate(modules):
        if i > 0:
            lines.append("---\n")

        module_name = module.path.split("/")[-1].replace(".py", "")
        lines.append(f"## {module_name}\n")

        if module.docstring:
            lines.append(module.docstring.strip())
            lines.append("\n")

        if module.classes:
            lines.append("### Classes\n")
            for cls in module.classes:
                lines.append(format_class(cls))
                lines.append("\n")

        if module.functions:
            lines.append("### Functions\n")
            for func in module.functions:
                lines.append(format_function(func))
                lines.append("\n")

    return "\n".join(lines)


def format_coverage_report(old_md: str, new_md: str) -> tuple[bool, str]:
    """Compare two markdown documents for API coverage."""
    old_symbols = _extract_symbols(old_md)
    new_symbols = _extract_symbols(new_md)

    added = new_symbols - old_symbols
    removed = old_symbols - new_symbols

    report_lines = []
    complete = len(removed) == 0

    if added:
        report_lines.append("## Added\n")
        for symbol in sorted(added):
            report_lines.append(f"+ {symbol}")
        report_lines.append("")

    if removed:
        report_lines.append("## Removed\n")
        for symbol in sorted(removed):
            report_lines.append(f"- {symbol}")
        report_lines.append("")

    return complete, "\n".join(report_lines)


def _extract_symbols(md: str) -> set:
    """Extract symbol names from markdown."""
    import re
    symbols = set()
    for match in re.findall(r"### `def\s+(\w+)", md):
        symbols.add(f"def:{match}")
    for match in re.findall(r"### `class\s+(\w+)", md):
        symbols.add(f"class:{match}")
    for match in re.findall(r"```\s*def\s+(\w+)", md):
        symbols.add(f"def:{match}")
    return symbols