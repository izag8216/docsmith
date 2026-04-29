"""Tests for CLI commands."""

import os
import pytest
import tempfile
from click.testing import CliRunner
from docsmith.cli import main


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_module():
    """Create a sample Python module for testing."""
    return '''"""Sample module for testing."""

def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number.
        b: Second number.

    Returns:
        The sum of a and b.
    """
    return a + b


class Calculator:
    """A calculator class."""

    def __init__(self):
        """Initialize the calculator."""
        self.result = 0

    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers.

        Args:
            x: First number.
            y: Second number.

        Returns:
            The product of x and y.
        """
        return x * y
'''


def test_cli_help(runner):
    """Test CLI help output."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "docsmith" in result.output
    assert "Lightweight" in result.output


def test_cli_version(runner):
    """Test CLI version output."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1" in result.output


def test_generate_single_module(runner, sample_module):
    """Test generate command for single module."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(sample_module)
        f.flush()
        filepath = f.name

    try:
        result = runner.invoke(main, ["generate", filepath])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "Calculator" in result.output
    finally:
        os.unlink(filepath)


def test_generate_with_output(runner, sample_module):
    """Test generate command with output file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(sample_module)
        f.flush()
        filepath = f.name

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as out:
        output_path = out.name

    try:
        result = runner.invoke(main, ["generate", filepath, "-o", output_path])
        assert result.exit_code == 0

        with open(output_path, "r") as f:
            content = f.read()
            assert "add" in content
    finally:
        os.unlink(filepath)
        os.unlink(output_path)


def test_single_command(runner, sample_module):
    """Test single command for single module."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(sample_module)
        f.flush()
        filepath = f.name

    try:
        result = runner.invoke(main, ["single", filepath])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "Calculator" in result.output
    finally:
        os.unlink(filepath)


def test_single_with_output(runner, sample_module):
    """Test single command with output."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(sample_module)
        f.flush()
        filepath = f.name

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as out:
        output_path = out.name

    try:
        result = runner.invoke(main, ["single", filepath, "-o", output_path])
        assert result.exit_code == 0

        with open(output_path, "r") as f:
            content = f.read()
            assert "add" in content
    finally:
        os.unlink(filepath)
        os.unlink(output_path)


def test_diff_command(runner):
    """Test diff command."""
    old_content = """# API Documentation

### `def add(a, b)`
"""

    new_content = """# API Documentation

### `def add(a, b)`
### `def multiply(x, y)`
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(old_content)
        f.flush()
        old_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(new_content)
        f.flush()
        new_path = f.name

    try:
        result = runner.invoke(main, ["diff", old_path, new_path])
        assert result.exit_code == 0
        assert "Added" in result.output
    finally:
        os.unlink(old_path)
        os.unlink(new_path)


def test_diff_check_coverage_pass(runner):
    """Test diff with --check-coverage when passing."""
    content = """### `def add(a, b)`
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        f.flush()
        filepath = f.name

    try:
        result = runner.invoke(main, ["diff", filepath, filepath, "--check-coverage"])
        assert result.exit_code == 0
    finally:
        os.unlink(filepath)


def test_diff_check_coverage_fail(runner):
    """Test diff with --check-coverage when failing."""
    old_content = """### `def add(a, b)`
### `def remove(x)`
"""
    new_content = """### `def add(a, b)`
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(old_content)
        f.flush()
        old_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(new_content)
        f.flush()
        new_path = f.name

    try:
        result = runner.invoke(main, ["diff", old_path, new_path, "--check-coverage"])
        assert result.exit_code == 1
    finally:
        os.unlink(old_path)
        os.unlink(new_path)


def test_init_command(runner):
    """Test init command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(main, ["init", tmpdir])
        assert result.exit_code == 0

        config_path = os.path.join(tmpdir, ".docsmith.toml")
        assert os.path.exists(config_path)

        with open(config_path, "r") as f:
            content = f.read()
            assert "docsmith" in content


def test_init_existing(runner):
    """Test init with existing config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, ".docsmith.toml")
        with open(config_path, "w") as f:
            f.write("existing config")

        result = runner.invoke(main, ["init", tmpdir])
        assert result.exit_code == 0
        assert "already exists" in result.output


def test_generate_directory(runner, sample_module):
    """Test generate command for directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        module_path = os.path.join(tmpdir, "sample_module.py")
        with open(module_path, "w") as f:
            f.write(sample_module)

        result = runner.invoke(main, ["generate", tmpdir, "-r"])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "Calculator" in result.output


def test_generate_nonexistent_path(runner):
    """Test generate with nonexistent path."""
    result = runner.invoke(main, ["generate", "/nonexistent/path"])
    assert result.exit_code != 0


def test_single_nonexistent_file(runner):
    """Test single with nonexistent file."""
    result = runner.invoke(main, ["single", "/nonexistent/file.py"])
    assert result.exit_code != 0