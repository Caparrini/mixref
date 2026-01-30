"""Tests for CLI entry point."""

from typer.testing import CliRunner

from mixref.cli.main import app

runner = CliRunner()


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
    assert "mixref version" in result.stdout
    assert "0.1.0" in result.stdout


def test_cli_version_short() -> None:
    """Test CLI -v flag."""
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout
