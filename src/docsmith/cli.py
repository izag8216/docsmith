"""CLI interface for docsmith."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from docsmith import __version__
from docsmith.parser import parse_module, parse_directory, ModuleDoc
from docsmith.formatter import format_module, format_modules, format_coverage_report
from docsmith.template import TemplateEngine


@click.group()
@click.version_option(version=__version__)
def main():
    """docsmith -- Lightweight docstring to Markdown documentation generator."""
    pass


@main.command("generate")
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["google", "numpy", "sphinx", "auto"]), default="auto", help="Docstring format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--template", "-t", type=click.Path(exists=True), help="Custom Jinja2 template")
@click.option("--recursive", "-r", is_flag=True, help="Process directories recursively")
def generate(path: str, format: str, output: str, template: str, recursive: bool):
    """Generate documentation for Python source files."""
    engine = TemplateEngine(template_path=template)

    if os.path.isdir(path):
        if recursive:
            modules = parse_directory(path)
        else:
            modules = []
            for filename in os.listdir(path):
                if filename.endswith(".py") and not filename.startswith("test_"):
                    modules.append(parse_module(os.path.join(path, filename)))

        if template:
            result = engine.render_modules(modules, template)
        else:
            result = format_modules(modules)
    else:
        module = parse_module(path)
        if template:
            result = engine.render_module(module, template)
        else:
            result = format_module(module)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        click.echo(f"Documentation written to {output}")
    else:
        click.echo(result)


@main.command("single")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["google", "numpy", "sphinx", "auto"]), default="auto")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--template", "-t", type=click.Path(exists=True), help="Custom Jinja2 template")
def single(filepath: str, format: str, output: str, template: str):
    """Generate documentation for a single module."""
    engine = TemplateEngine(template_path=template)
    module = parse_module(filepath)

    if template:
        result = engine.render_module(module, template)
    else:
        result = format_module(module)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        click.echo(f"Documentation written to {output}")
    else:
        click.echo(result)


@main.command("serve")
@click.argument("path", type=click.Path(exists=True))
@click.option("--port", "-p", type=int, default=8090, help="Port to serve on")
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--template", "-t", type=click.Path(exists=True), help="Custom Jinja2 template")
def serve(path: str, port: int, host: str, template: str):
    """Serve documentation with live reload."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        click.echo("Error: watchdog required for serve command. Install with: pip install docsmith[dev]", err=True)
        sys.exit(1)

    engine = TemplateEngine(template_path=template)
    output_path = "/tmp/docsmith_output.md"

    def generate_docs():
        if os.path.isdir(path):
            modules = parse_directory(path)
            result = engine.render_modules(modules, template) if template else format_modules(modules)
        else:
            module = parse_module(path)
            result = engine.render_module(module, template) if template else format_module(module)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)

    class DocsHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith(".py"):
                generate_docs()

    generate_docs()

    try:
        from http.server import HTTPServer
        import webbrowser

        handler = lambda *args: None

        observer = Observer()
        observer.schedule(DocsHandler(), path, recursive=True)
        observer.start()

        url = f"http://{host}:{port}"
        click.echo(f"Serving documentation at {url}")
        click.echo(f"Output: {output_path}")
        click.echo("Press Ctrl+C to stop")

        webbrowser.open(url)

        server = HTTPServer((host, port), handler)
        server.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


@main.command("diff")
@click.argument("old", type=click.Path(exists=True))
@click.argument("new", type=click.Path(exists=True))
@click.option("--check-coverage", is_flag=True, help="Exit with error if coverage decreased")
def diff(old: str, new: str, check_coverage: bool):
    """Compare two documentation files for API surface changes."""
    with open(old, "r", encoding="utf-8") as f:
        old_md = f.read()

    with open(new, "r", encoding="utf-8") as f:
        new_md = f.read()

    complete, report = format_coverage_report(old_md, new_md)

    if report:
        click.echo(report)
    else:
        click.echo("No changes detected.")

    if check_coverage and not complete:
        click.echo("\nCoverage check FAILED: API surface changed.", err=True)
        sys.exit(1)


@main.command("init")
@click.argument("path", type=click.Path(), default=".")
def init(path: str):
    """Initialize a docsmith configuration in the current directory."""
    config_path = os.path.join(path, ".docsmith.toml")

    if os.path.exists(config_path):
        click.echo(f"Configuration already exists at {config_path}")
        return

    default_config = """[docsmith]
format = "google"
output = "docs/api.md"
template = "docs/template.j2"

[docsmith.generate]
recursive = true
include_private = false
"""
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(default_config)

    click.echo(f"Configuration written to {config_path}")


if __name__ == "__main__":
    main()