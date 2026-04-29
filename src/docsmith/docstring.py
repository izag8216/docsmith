"""Docstring format detection and parsing."""

from __future__ import annotations

import re
from enum import Enum


class DocstringFormat(Enum):
    """Supported docstring formats."""

    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    AUTO = "auto"


def detect_format(docstring: str) -> DocstringFormat:
    """Detect docstring format from content."""
    if not docstring:
        return DocstringFormat.GOOGLE

    first_block = docstring.strip().split("\n")[:15]
    text = "\n".join(first_block).lower()

    if re.search(r"parameters\s*\n\s*-{3,}", text):
        return DocstringFormat.NUMPY
    elif ":param" in text or ":type" in text or ":return" in text or ":raises" in text:
        return DocstringFormat.SPHINX
    elif "args:" in text or "arguments:" in text:
        return DocstringFormat.GOOGLE

    return DocstringFormat.GOOGLE


def parse(docstring: str, format: DocstringFormat = DocstringFormat.AUTO) -> dict:
    """Parse docstring into structured dictionary."""
    if format == DocstringFormat.AUTO:
        format = detect_format(docstring)

    if format == DocstringFormat.NUMPY:
        return _parse_numpy(docstring)
    elif format == DocstringFormat.SPHINX:
        return _parse_sphinx(docstring)
    else:
        return _parse_google(docstring)


def _parse_google(docstring: str) -> dict:
    """Parse Google-style docstring."""
    if not docstring:
        return {"description": "", "args": [], "returns": None, "raises": [], "examples": None}

    result = {"description": "", "args": [], "returns": None, "raises": [], "examples": None}
    lines = docstring.strip().split("\n")

    current_section = "description"
    section_content = []
    desc_lines = []

    for line in lines:
        stripped = line.strip()
        stripped_lower = stripped.lower()

        if stripped_lower.startswith("args:") or stripped_lower.startswith("arguments:"):
            if current_section == "description":
                result["description"] = "\n".join(desc_lines).strip()
            current_section = "args"
            section_content = []
        elif stripped_lower.startswith("returns:") or stripped_lower.startswith("return:"):
            if current_section == "args" and section_content:
                result["args"] = _extract_google_args(section_content)
            current_section = "returns"
            section_content = []
        elif stripped_lower.startswith("raises:"):
            if current_section == "returns" and section_content:
                result["returns"] = "\n".join(section_content).strip()
            elif current_section == "args" and section_content:
                result["args"] = _extract_google_args(section_content)
            current_section = "raises"
            section_content = []
        elif stripped_lower.startswith("example:"):
            if current_section == "raises" and section_content:
                result["raises"] = [r.strip() for r in "\n".join(section_content).split(",")]
            current_section = "examples"
            section_content = []
        elif current_section == "description":
            desc_lines.append(stripped)
        else:
            section_content.append(stripped)

    if current_section == "args" and section_content:
        result["args"] = _extract_google_args(section_content)
    elif current_section == "returns" and section_content:
        result["returns"] = "\n".join(section_content).strip()
    elif current_section == "raises" and section_content:
        result["raises"] = [r.strip() for r in "\n".join(section_content).split(",")]

    if not result["description"] and desc_lines:
        result["description"] = "\n".join(desc_lines).strip()

    return result


def _extract_google_args(lines: list[str]) -> list[tuple[str, str]]:
    """Extract argument descriptions from Google-style args section."""
    args = []
    current_arg = None
    current_desc = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if ":" in stripped:
            if current_arg:
                args.append((current_arg, " ".join(current_desc).strip()))
            parts = stripped.split(":", 1)
            current_arg = parts[0].strip()
            current_desc = [parts[1].strip()] if len(parts) > 1 and parts[1].strip() else []
        elif current_arg:
            current_desc.append(stripped)

    if current_arg:
        args.append((current_arg, " ".join(current_desc).strip()))

    return args


def _parse_numpy(docstring: str) -> dict:
    """Parse NumPy-style docstring."""
    if not docstring:
        return {"description": "", "args": [], "returns": None, "raises": [], "examples": None}

    result = {"description": "", "args": [], "returns": None, "raises": [], "examples": None}
    lines = docstring.strip().split("\n")

    desc_lines = []
    in_params = False
    in_returns = False
    params_content = []
    returns_content = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("Parameters"):
            in_params = True
            result["description"] = "\n".join(desc_lines).strip()
            desc_lines = []
        elif stripped.startswith("Returns"):
            in_params = False
            in_returns = True
            if params_content:
                result["args"] = _extract_numpy_params(params_content)
            params_content = []
        elif stripped.startswith("---") or stripped.startswith("==="):
            pass
        elif in_params:
            params_content.append(stripped)
        elif in_returns:
            returns_content.append(stripped)
        elif stripped:
            desc_lines.append(stripped)

    if params_content and not result["args"]:
        result["args"] = _extract_numpy_params(params_content)
    if returns_content:
        result["returns"] = "\n".join(returns_content).strip()

    if not result["description"]:
        result["description"] = "\n".join(desc_lines).strip()

    return result


def _extract_numpy_params(lines: list[str]) -> list[tuple[str, str]]:
    """Extract parameter descriptions from NumPy-style section."""
    args = []
    current_arg = None
    current_desc = []
    expect_description = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if ":" in stripped and not stripped.startswith(" " * 4):
            if current_arg:
                args.append((current_arg, " ".join(current_desc).strip()))
            parts = stripped.split(":", 1)
            current_arg = parts[0].strip()
            desc_part = parts[1].strip() if len(parts) > 1 else ""

            common_types = ("int", "str", "float", "bool", "list", "dict", "tuple", "None", "any", "array", "object", "type", "dtype", "ndarray")
            if desc_part in common_types or desc_part.startswith("type ") or desc_part.startswith("dtype"):
                current_desc = []
                expect_description = True
            else:
                current_desc = [desc_part]
                expect_description = False
        elif current_arg and expect_description and stripped:
            current_desc.append(stripped)
            expect_description = False
        elif current_arg:
            if current_desc:
                current_desc.append(stripped)
            else:
                expect_description = True

    if current_arg:
        args.append((current_arg, " ".join(current_desc).strip()))

    return args


def _parse_sphinx(docstring: str) -> dict:
    """Parse Sphinx-style docstring."""
    if not docstring:
        return {"description": "", "args": [], "returns": None, "raises": [], "examples": None}

    result = {"description": "", "args": [], "returns": None, "raises": [], "examples": None}
    lines = docstring.strip().split("\n")

    desc_lines = []
    args = []
    returns_val = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith(":param"):
            colon_count = stripped.count(":")
            if colon_count >= 2:
                parts = stripped[6:].split(":", 1)
                if len(parts) == 2:
                    param_name = parts[0].strip()
                    param_desc = parts[1].strip()
                    if param_name:
                        args.append((param_name, param_desc))
        elif stripped.startswith(":type"):
            pass
        elif stripped.startswith(":return") or stripped.startswith(":returns"):
            colon_count = stripped.count(":")
            if colon_count >= 2:
                colon_idx = stripped.find(":")
                after_first = stripped[colon_idx + 1:]
                colon_idx2 = after_first.find(":")
                if colon_idx2 >= 0:
                    returns_val = after_first[colon_idx2 + 1:].strip()
        elif stripped.startswith(":raises"):
            colon_count = stripped.count(":")
            if colon_count >= 2:
                colon_idx = stripped.find(":")
                after_first = stripped[colon_idx + 1:]
                colon_idx2 = after_first.find(":")
                if colon_idx2 >= 0:
                    result["raises"].append(after_first[colon_idx2 + 1:].strip())
        elif not stripped.startswith(":"):
            desc_lines.append(stripped)

    result["args"] = args
    result["returns"] = returns_val
    result["description"] = "\n".join(desc_lines).strip()

    return result