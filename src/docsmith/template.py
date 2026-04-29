"""Jinja2 template engine for docsmith."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, BaseLoader
from jinja2 import select_autoescape, Environment

from docsmith.parser import ModuleDoc, ClassDoc, FunctionDoc


class DocsmithLoader(BaseLoader):
    """Custom Jinja2 loader for docsmith templates."""

    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir

    def get_source(self, environment, template):
        if self.template_dir and os.path.isabs(template):
            path = template
        elif self.template_dir:
            path = os.path.join(self.template_dir, template)
        else:
            path = template

        if not os.path.exists(path):
            raise FileNotFoundError(f"Template not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        return source, path, lambda: True


class TemplateEngine:
    """Jinja2 template rendering engine for docsmith."""

    def __init__(self, template_dir: Optional[str] = None, template_path: Optional[str] = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "..", "templates")
        self.template_path = template_path

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir) if self.template_dir else None,
            autoescape=select_autoescape(default=False),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self.env.filters["format_args"] = self._format_args_filter
        self.env.filters["class_name"] = self._class_name_filter
        self.env.filters["docstring_first_line"] = self._docstring_first_line_filter

    @staticmethod
    def _format_args_filter(args: list) -> str:
        """Format function arguments as a string."""
        parts = []
        for arg in args:
            if arg.default:
                parts.append(f"{arg.name}={arg.default}")
            elif arg.annotation:
                parts.append(f"{arg.name}: {arg.annotation}")
            else:
                parts.append(arg.name)
        return ", ".join(parts)

    @staticmethod
    def _class_name_filter(cls: ClassDoc) -> str:
        """Format class name with bases."""
        name = cls.name
        if cls.bases:
            bases_str = ", ".join(cls.bases)
            name += f"({bases_str})"
        return name

    @staticmethod
    def _docstring_first_line_filter(docstring: str) -> str:
        """Get the first line of a docstring."""
        if not docstring:
            return ""
        return docstring.strip().split("\n")[0]

    def render(self, template_name: str, context: dict) -> str:
        """Render a template with the given context."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_string(self, template_string: str, context: dict) -> str:
        """Render a template string with the given context."""
        template = self.env.from_string(template_string)
        return template.render(**context)

    def render_module(self, module: ModuleDoc, template_path: Optional[str] = None) -> str:
        """Render a module using a template."""
        if template_path:
            with open(template_path, "r", encoding="utf-8") as f:
                template = self.env.from_string(f.read())
        elif self.template_path:
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = self.env.from_string(f.read())
        else:
            default_template = os.path.join(os.path.dirname(__file__), "templates", "default.j2")
            if os.path.exists(default_template):
                template = self.env.get_template("default.j2")
            else:
                template = self.env.from_string(DEFAULT_TEMPLATE)

        context = {
            "module": module,
            "modules": [module],
        }
        return template.render(**context)

    def render_modules(self, modules: list[ModuleDoc], template_path: Optional[str] = None) -> str:
        """Render multiple modules using a template."""
        if template_path:
            with open(template_path, "r", encoding="utf-8") as f:
                template = self.env.from_string(f.read())
        elif self.template_path:
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = self.env.from_string(f.read())
        else:
            default_template = os.path.join(os.path.dirname(__file__), "templates", "default.j2")
            if os.path.exists(default_template):
                template = self.env.get_template("default.j2")
            else:
                template = self.env.from_string(DEFAULT_TEMPLATE)

        context = {
            "modules": modules,
        }
        return template.render(**context)


DEFAULT_TEMPLATE = """# API Documentation

{% for module in modules %}
## {{ module.path.split('/')[-1].replace('.py', '') }}

{% if module.docstring %}
{{ module.docstring }}
{% endif %}

{% if module.classes %}
### Classes

{% for cls in module.classes %}
#### {{ cls.name }}{% if cls.bases %}({{ cls.bases|join(', ') }}){% endif %}

{% if cls.docstring %}
{{ cls.docstring }}
{% endif %}

{% if cls.methods %}
**Methods:**

{% for method in cls.methods %}
- `{{ method.name }}({{ method.args|format_args }}){% if method.returns %}{{ ' -> ' + method.returns }}{% endif %}`
{% endfor %}
{% endif %}

---
{% endfor %}
{% endif %}

{% if module.functions %}
### Functions

{% for func in module.functions %}
#### `{{ func.name }}({{ func.args|format_args }}){% if func.returns %}{{ ' -> ' + func.returns }}{% endif %}`

{% if func.docstring %}
{{ func.docstring }}
{% endif %}

{% if func.args %}
**Parameters:**
{% for arg in func.args %}
- `{{ arg.name }}{% if arg.annotation %}: {{ arg.annotation }}{% endif %}`
{% endfor %}
{% endif %}

---
{% endfor %}
{% endif %}

{% endfor %}

{% endfor %}
"""