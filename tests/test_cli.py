"""Tests for CLI entry point."""

import re

from typer.testing import CliRunner

from mixref import __version__
from mixref.cli.main import app

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    """Strip ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


def test_cli_help() -> None:
    """Test CLI --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CLI Audio Analyzer" in result.stdout
    assert "Music Producers" in result.stdout


def test_cli_version() -> None:
    """Test CLI --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    output = _strip_ansi(result.stdout)
    assert "mixref version" in output
    assert __version__ in output


def test_cli_version_short() -> None:
    """Test CLI -v flag."""
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    output = _strip_ansi(result.stdout)
    assert __version__ in output
